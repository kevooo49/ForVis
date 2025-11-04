import {Component, Inject, OnInit} from '@angular/core';
import {User} from '../../model/user';
import {AUTH_SERVICE, IAuthService} from '../../services/interfaces/auth-service';
import {ALERT_SERVICE, IAlertService} from '../../services/interfaces/alert-service';
import {IUserService, USER_SERVICE} from '../../services/interfaces/user-service';
import {Router} from '@angular/router';
import {FormsModule} from '@angular/forms';
import {NgIf} from '@angular/common';

@Component({
  selector: 'app-account-edit',
  imports: [
    FormsModule,
    NgIf
  ],
  templateUrl: './account-edit.component.html',
  styleUrl: './account-edit.component.css'
})
export class AccountEditComponent implements OnInit {
  user: User = {
    username: '',
    name: '',
    password: '',
    email: '',
    firstname: '',
    lastname: '',
    recaptcha: ''
  }
  oldUser?: User;
  oldPassword: string = '';

  constructor(
    @Inject(USER_SERVICE) private userService: IUserService,
    @Inject(AUTH_SERVICE) private authService: IAuthService,
    @Inject(ALERT_SERVICE) private alertService: IAlertService,
    private router: Router) { }

  ngOnInit() {
    this.userService.getUser().subscribe({
      next: user => {
         this.oldUser = {
           username: user.username,
           name: user.name,
           email:  user.email,
           firstname: user.firstname,
           lastname: user.lastname
        }
      }
    });
  }

  submit() {
    if (this.oldUser) {
      let oldUserVerify = {
        username: this.oldUser.username,
        password: this.oldPassword
      }

      this.authService.tokenAuth(oldUserVerify).subscribe({
        next: () => {
          this.userService.editUser(this.user).subscribe({
            next: () => this.router.navigate(['sat']),
            error: err => this.alertService.error(err)
          })
        }
      });
    }
  }
}
