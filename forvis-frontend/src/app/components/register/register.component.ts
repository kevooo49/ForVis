import {Component, Inject, Injectable} from '@angular/core';
import {User} from '../../model/user';
import {Router} from '@angular/router';
import {IRegistrationService, REGISTRATION_SERVICE} from '../../services/interfaces/registration-service';
import {ALERT_SERVICE, IAlertService} from '../../services/interfaces/alert-service';
import {FormsModule} from '@angular/forms';
import {NgIf} from '@angular/common';
import {HttpClient} from '@angular/common/http';

@Component({
  selector: 'app-register',
  imports: [
    FormsModule,
    NgIf
  ],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css',
  providers: [

  ]
})
export class RegisterComponent {
  user: User = {
    name: '',
    password: '',
    email: '',
    firstname: '',
    lastname: '',
    recaptcha: 'success',
    username: ''
  };

  constructor(
    @Inject(REGISTRATION_SERVICE) private registrationService: IRegistrationService,
    @Inject(ALERT_SERVICE) private alertService: IAlertService,
    private router: Router) {
  }

  register() {
    console.log("kajwndkjawd");
    this.user.username = this.user.email;
    if (this.user) {
      this.registrationService.register(this.user).subscribe({
        next: () => {
          this.router.navigate(['login']).then();
        },
        error: (err) => {
          this.alertService.error(err);
        }
      });
    }
  }
}
