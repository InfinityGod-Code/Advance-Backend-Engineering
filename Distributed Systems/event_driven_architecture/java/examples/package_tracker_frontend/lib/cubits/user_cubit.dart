import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../models/user.dart';
import '../services/user_service.dart';

abstract class UserState extends Equatable {
  const UserState();
}

class UserInitial extends UserState {
  const UserInitial();
  @override
  List<Object?> get props => [];
}

class UserLoading extends UserState {
  const UserLoading();
  @override
  List<Object?> get props => [];
}

class UserLoaded extends UserState {
  final List<User> users;
  const UserLoaded(this.users);
  @override
  List<Object?> get props => [users];
}

class UserError extends UserState {
  final String message;
  const UserError(this.message);
  @override
  List<Object?> get props => [message];
}

class UserCubit extends Cubit<UserState> {
  final UserService _service = UserService();

  UserCubit() : super(const UserInitial());

  Future<void> loadUsers() async {
    emit(const UserLoading());
    try {
      final users = await _service.getUsers();
      emit(UserLoaded(users));
    } catch (e) {
      emit(UserError('Failed to load users: $e'));
    }
  }

  Future<void> createUser(Map<String, dynamic> body) async {
    final current = state;
    try {
      final user = await _service.createUser(body);
      if (current is UserLoaded) {
        emit(UserLoaded([...current.users, user]));
      } else {
        await loadUsers();
      }
    } catch (e) {
      emit(UserError('Failed to create user: $e'));
    }
  }
}
