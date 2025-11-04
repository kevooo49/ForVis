import {Inject, Injectable} from '@angular/core';
import {IUserService} from '../interfaces/user-service';
import {User} from '../../model/user';
import {Observable} from 'rxjs';
import {HttpClient} from '@angular/common/http';
import {Environment} from '../../environments/environment';
import {AUTH_SERVICE, IAuthService} from '../interfaces/auth-service';
import {map} from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class UserService implements IUserService {
  private baseUrl = `${Environment.baseUrl}/profile`;

  constructor(
    @Inject(AUTH_SERVICE) private authService: IAuthService,
    private http: HttpClient)
  { }

  editUser(user: User): Observable<User> {
      return this.http.put<User>(`${this.baseUrl}/user`, user, this.authService.authOptions());
  }

  getUser(): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/user`, this.authService.authOptions()).pipe(
      map((response: User) => response)
    );
  }
}
