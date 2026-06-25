class Address {
  final String street;
  final String city;
  final String state;
  final String zipCode;
  final String country;

  Address({
    required this.street,
    required this.city,
    required this.state,
    required this.zipCode,
    required this.country,
  });

  String get fullAddress => '$street, $city, $state $zipCode, $country';
  String get shortAddress => '$city, $state';
}
