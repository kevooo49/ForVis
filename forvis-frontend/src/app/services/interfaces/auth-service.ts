import {InjectionToken} from '@angular/core';
import {User} from '../../model/user';
import {Observable} from 'rxjs';
import {HttpHeaders} from '@angular/common/http';
import {Authentication} from '../../model/authentication';

export const AUTH_SERVICE = new InjectionToken<IAuthService>('LoginService');

export interface IAuthService {
  get authenticated(): Observable<boolean>;

  authOptions(options?: Object, headers?: HttpHeaders): { headers: HttpHeaders };

  tokenAuth(user: Authentication): Observable<any>;

  tokenRefresh(): Observable<any>;

  tokenVerify(): Observable<boolean>;

  logout(): void;

  getAuthTokenString(): string | null;
}
