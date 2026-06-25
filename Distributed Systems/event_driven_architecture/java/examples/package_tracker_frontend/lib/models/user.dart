import 'package:flutter/material.dart';
import 'address.dart';

class User {
  final String id;
  final String name;
  final String email;
  final String phone;
  final Address address;
  final Color avatarColor;
  final DateTime createdAt;

  User({
    required this.id,
    required this.name,
    required this.email,
    required this.phone,
    required this.address,
    required this.avatarColor,
    required this.createdAt,
  });

  String get initials {
    final parts = name.split(' ');
    if (parts.length >= 2) return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    return name.isNotEmpty ? name[0].toUpperCase() : '?';
  }
}
