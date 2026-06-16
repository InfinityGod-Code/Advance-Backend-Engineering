from fastapi import FastAPI
import pyotp
import qrcode
from io import BytesIO
from fastapi import  HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app_description = """
Open MFA standards are defined in RFC 4226 (HOTP: An HMAC-Based One-Time Password Algorithm)
and in RFC 6238 (TOTP: Time-Based One-Time Password Algorithm). PyOTP implements server-side
support for both of these standards. Client-side support can be enabled by sending authentication
codes to users over SMS or email (HOTP) or, for TOTP, by instructing users to use Google Authenticator,
Authy, or another compatible app.
"""

app = FastAPI(title="MFA using the TOTP",description=app_description)


# 1. Models & Schemas
class UserCreate(BaseModel):
    username: str
    password: str  # In production, this must be hashed.

class LoginRequest(BaseModel):
    username: str
    password: str
    totp_token: str

class UserInDB:
    def __init__(self, username, hashed_password):
        self.username = username
        self.hashed_password = hashed_password
        self.mfa_secret = None  # Encrypted at rest in prod
        self.mfa_enabled = False

# MOCK DB (For demonstration)
mock_db = {}

# --- Helper Functions ---

def encrypt_secret(secret: str) -> str:
    # Senior Staff reminder: Implement strong symmetric encryption here (e.g., Fernet).
    # NEVER store raw shared secrets in the database.
    return f"ENCRYPTED_{secret}"

def decrypt_secret(encrypted_secret: str) -> str:
    # Reverse the encryption
    return encrypted_secret.replace("ENCRYPTED_", "")

# --- 2. Registration Flow ---

@app.post("/register/begin", summary="1. Generate MFA Secret & QR Code")
def register_mfa_begin(user: UserCreate):
    """
    Step 1: User registers. We generate a unique secret just for them.
    We return a QR code image that their authenticator app scans.
    """
    if user.username in mock_db:
        raise HTTPException(status_code=400, detail="User exists")

    # A. Create the user object
    # In prod, hash the password: hashed_pw = pwd_context.hash(user.password)
    new_user = UserInDB(user.username, user.password)
    mock_db[user.username] = new_user

    # B. Generate a base32, random shared secret (RFC 6238 standard)
    # Senior Staff note: This secret must be securely random.
    new_secret = pyotp.random_base32()
    
    # C. SECURELY STORE the secret. Encrypt it before saving to DB.
    new_user.mfa_secret = encrypt_secret(new_secret)
    # mock_db[user.username].save() in real DB

    # D. Generate the provisioning URI (the data that makes the QR code)
    # format: 'otpauth://totp/Issuer:AccountName?secret=SECRET&issuer=Issuer'
    provisioning_uri = pyotp.totp.TOTP(new_secret).provisioning_uri(
        name=user.username, 
        issuer_name="MyFastAPISecureApp"
    )

    # E. Generate the QR Code image on the fly (don't save it to disk)
    img = qrcode.make(provisioning_uri)
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    
    return StreamingResponse(buf, media_type="image/png")


# --- 3. Verification/Login Flow ---

@app.post("/login", summary="2. Authenticate with Password + TOTP")
def login_with_mfa(request: LoginRequest):
    """
    Step 2: User logs in with primary password and the secondary TOTP token.
    """
    user_data = mock_db.get(request.username)
    
    # A. Validate Primary Credential (simplified)
    # In prod: if not pwd_context.verify(request.password, user_data.hashed_password):
    if not user_data or request.password != user_data.hashed_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # B. If MFA is enabled, validate the TOTP token
    if user_data.mfa_secret:
        # 1. Retrieve and decrypt the shared secret from storage
        decrypted_secret = decrypt_secret(user_data.mfa_secret)
        
        # 2. Instantiate the TOTP calculator using the *decrypted* secret
        totp = pyotp.TOTP(decrypted_secret)

        # 3. VERIFY: Compare the user-provided token against the calculated token.
        # pyotp.verify() handles time-step alignment (handling slight clock drift).
        is_valid = totp.verify(request.totp_token)
        
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid MFA token")
        
        # Optionally mark MFA as 'fully set up' after the first successful check
        if not user_data.mfa_enabled:
            user_data.mfa_enabled = True # In real DB: user_data.save()

    # C. Login successful (Generate JWT, set session, etc.)
    return {"message": "Login successful!", "mfa_authenticated": True if user_data.mfa_secret else False}

@app.get("/")
def test() :
    return {
        "content" : "Hello World"
    }