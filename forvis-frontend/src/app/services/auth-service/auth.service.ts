import { Injectable } from '@angular/core';
import { IAuthService } from '../interfaces/auth-service';
import { User } from '../../model/user';
import { Observable, BehaviorSubject } from 'rxjs';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Environment } from '../../environments/environment';
import { map, catchError } from 'rxjs/operators';
import { of } from 'rxjs';
import {Authentication} from '../../model/authentication';

@Injectable({
  providedIn: 'root'
})
export class AuthService implements IAuthService {
  private baseUrl = `${Environment.baseUrl}/auth`;
  private authenticated$ = new BehaviorSubject<boolean>(false);

  constructor(private http: HttpClient) {
    const token = this.getToken();
    if (token) {
      this.verifyTokenOnInit(token);
    }
  }

  get authenticated(): Observable<boolean> {
    return this.authenticated$.asObservable();
  }

  private getToken(): string | null {
    return localStorage.getItem('token');
  }

  private verifyTokenOnInit(token: string): void {
    this.http.post(`${this.baseUrl}/api-token-verify/`, { token }).pipe(
      map(() => {
        this.authenticated$.next(true);
      }),
      catchError(() => {
        this.authenticated$.next(false);
        localStorage.removeItem('token');
        return of(false);
      })
    ).subscribe();
  }  

  private setAuthHeaders(headers: HttpHeaders = new HttpHeaders()): HttpHeaders {
    const token = this.getToken();
    if (token) {
      return headers.append('Authorization', 'JWT ' + token);
    }
    return headers;
  }

  authOptions(options: any = {}, headers: HttpHeaders = new HttpHeaders()): any {
    const finalHeaders = this.setAuthHeaders(headers);
    return {
      ...options,
      headers: finalHeaders
    };
  }

  tokenAuth(user: Authentication): Observable<any> {
    const body = { username: user.username, password: user.password };

    return this.http.post<any>(`${this.baseUrl}/api-token-auth/`, body).pipe(
      map(response => {
        localStorage.setItem('token', response.token);
        this.authenticated$.next(true);
        return response;
      }),
      catchError(error => {
        this.authenticated$.next(false);
        return of(error);
      })
    );
  }

  tokenRefresh(): Observable<any> {
    const token = this.getToken();
    if (!token) {
      return of(null);
    }

    return this.http.post<any>(`${this.baseUrl}/api-token-refresh/`, { token }).pipe(
      map(response => {
        localStorage.setItem('token', response.token);
        this.authenticated$.next(true);
        return response;
      }),
      catchError(error => {
        this.logout();
        return of(error);
      })
    );
  }

  tokenVerify(): Observable<boolean> {
    const token = this.getToken();
    if (!token) {
      this.authenticated$.next(false);
      return of(false);
    }

    return this.http.post<any>(`${this.baseUrl}/api-token-verify/`, { token }).pipe(
      map(response => {
        // jeśli backend zwróci 200 OK – token poprawny
        this.authenticated$.next(true);
        return true;
      }),
      catchError(error => {
        console.warn('Token verification failed:', error);
        this.authenticated$.next(false);
        return of(false);
      })
    );
  }


  logout(): void {
    this.authenticated$.next(false);
    localStorage.clear();
  }

  getAuthTokenString(): string | null {
    return this.getToken() ? 'JWT ' + this.getToken() : null;
  }

  isAuthenticated(): Observable<boolean> {
    return this.authenticated$.asObservable();
  }
}