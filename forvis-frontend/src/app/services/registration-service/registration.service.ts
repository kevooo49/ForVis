import { Injectable } from '@angular/core';
import {IRegistrationService} from '../interfaces/registration-service';
import {User} from '../../model/user';
import {Observable} from 'rxjs';
import { HttpClient } from '@angular/common/http';
import {Environment} from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class RegistrationService implements IRegistrationService {
  private baseUrl = `${Environment.baseUrl}/profile`;

  constructor(private http: HttpClient) { }

  register(user: User): Observable<boolean> {
    return this.http.post<boolean>(`${this.baseUrl}/register/`, user, );
  }
}
