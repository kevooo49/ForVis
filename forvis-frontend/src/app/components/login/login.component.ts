import { Component, Inject } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { User } from '../../model/user';
import { ALERT_SERVICE, IAlertService } from '../../services/interfaces/alert-service';
import { AUTH_SERVICE, IAuthService } from '../../services/interfaces/auth-service';
import {FormsModule} from '@angular/forms';
import {NgIf} from '@angular/common';
import {Authentication} from '../../model/authentication';

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
    private route: ActivatedRoute) { }

  login(): void {
    const returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/cnf-uploader';

    this.authService.tokenAuth(this.user).subscribe({
      next: (response) => {
        if (response && response.token) {
          console.log('Login successful');
          this.router.navigateByUrl(returnUrl);
        } else {
          this.alertService.error('Invalid username or password');
        }
      },
      error: (error) => {
        console.error('Login error:', error);
        this.alertService.error('Login failed. Please check your credentials.');
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