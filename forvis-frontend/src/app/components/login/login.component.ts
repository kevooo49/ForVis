import { Component, Inject } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { ALERT_SERVICE, IAlertService } from '../../services/interfaces/alert-service';
import { AUTH_SERVICE, IAuthService } from '../../services/interfaces/auth-service';
import { FormsModule } from '@angular/forms';
import { NgIf } from '@angular/common';
import { Authentication } from '../../model/authentication';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  imports: [
    FormsModule,
    NgIf
  ],
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  user: Authentication = {
    username: '',
    password: ''
  };

  constructor(
    @Inject(AUTH_SERVICE) private authService: IAuthService,
    @Inject(ALERT_SERVICE) private alertService: IAlertService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  login(): void {
    const returnUrl = this.route.snapshot.queryParams['returnUrl'] || 'sat';

    this.authService.tokenAuth(this.user).subscribe({
      next: (response) => {
        if (response && response.token) {
          // ✅ Tylko jeśli backend faktycznie zwrócił token
          this.router.navigate([returnUrl]);
        } else {
          // ❌ Nieprawidłowe dane logowania lub brak tokena
          this.alertService.error('Invalid username or password');
        }
      },
      error: (error) => {
        console.error('Login failed:', error);
        this.alertService.error('Login failed. Please try again.');
      }
    });
  }

  goToRegistration(): void {
    this.router.navigate(['register']).then(() => {
      console.log('Navigated to registration page!');
    }).catch(error => {
      console.error('Navigation failed', error);
    });
  }
}
