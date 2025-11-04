import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import {NavbarComponent} from './components/navbar/navbar.component';
import {REGISTRATION_SERVICE} from './services/interfaces/registration-service';
import {ALERT_SERVICE} from './services/interfaces/alert-service';
import {AUTH_SERVICE} from './services/interfaces/auth-service';
import {AuthService} from './services/auth-service/auth.service';
import {AlertService} from './services/alert-service/alert.service';
import {RegistrationService} from './services/registration-service/registration.service';
import {USER_SERVICE} from './services/interfaces/user-service';
import {UserService} from './services/user-service/user.service';
import {VIS_MENU_SERVICE} from "./services/interfaces/vis-menu-service";
import {VisMenuService} from "./services/vis-menu-service/vis-menu.service";
import {FILE_SERVICE} from "./services/interfaces/file-service";
import {FileService} from "./services/file-service/file.service";
import {JSON_FILE_SERVICE} from "./services/interfaces/json-file-service";
import {JsonFileService} from "./services/json-file-service/json-file.service";

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, NavbarComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
  providers: [
    { provide: REGISTRATION_SERVICE, useClass: RegistrationService },
    { provide: ALERT_SERVICE, useClass: AlertService },
    { provide: AUTH_SERVICE, useClass: AuthService },
    { provide: USER_SERVICE, useClass: UserService },
    { provide: VIS_MENU_SERVICE, useClass: VisMenuService },
    { provide: FILE_SERVICE, useClass: FileService },
    { provide: JSON_FILE_SERVICE, useClass: JsonFileService },
  ]
})
export class AppComponent {

}
