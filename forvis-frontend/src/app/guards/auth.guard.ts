import { Injectable } from '@angular/core';
import { CanActivate, Router, UrlTree } from '@angular/router';
import { Observable, of } from 'rxjs';
import { AuthService } from '../services/auth-service/auth.service';
import { catchError, map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) {}

  canActivate(): Observable<boolean | UrlTree> {
    return this.authService.tokenVerify().pipe(
      map(isAuth => {
        if (isAuth) {
          return true;
        } else {
          return this.router.createUrlTree(['/login'], {
            queryParams: { returnUrl: '/cnf-uploader' }
          });
        }
      }),
      catchError(() =>
        of(this.router.createUrlTree(['/login'], { queryParams: { returnUrl: '/cnf-uploader' } }))
      )
    );
  }
}
