import {InjectionToken} from '@angular/core';
import {User} from '../../model/user';
import {Observable} from 'rxjs';

export const USER_SERVICE = new InjectionToken<IUserService>('JsonFileService');

export interface IUserService {
  getUser(): Observable<User>;

  editUser(user: User): Observable<User>;
}
