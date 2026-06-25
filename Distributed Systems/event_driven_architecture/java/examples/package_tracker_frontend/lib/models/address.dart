class Address {
  final String? street;
  final String? city;
  final String? state;
  final String? zip;

  const Address({
    required this.street,
    required this.city,
    required this.state,
    required this.zip,
  });

  String get fullAddress => '$street, $city, $state $zip';
  String get shortAddress => '$city, $state';

  factory Address.fromJson(Map<String, dynamic> json) => Address(
    street: json['street'] as String?,
    city: json['city'] as String?,
    state: json['state'] as String?,
    zip: json['zip'] as String?,
  );

  Map<String, dynamic> toJson() => {
    'street': street,
    'city': city,
    'state': state,
    'zip': zip,
  };
}
