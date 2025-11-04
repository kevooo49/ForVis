import {User} from '../../model/user';
import {Observable} from 'rxjs';
import {InjectionToken} from '@angular/core';

export const REGISTRATION_SERVICE = new InjectionToken<IRegistrationService>('RegistrationService');

export interface IRegistrationService {
  register(user: User): Observable<boolean>;
}
