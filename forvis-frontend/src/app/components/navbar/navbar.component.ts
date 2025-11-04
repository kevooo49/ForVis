import {Component, Inject, OnInit} from '@angular/core';
import {Router, RouterLink, RouterLinkActive} from '@angular/router';
import {AsyncPipe, NgClass, NgIf} from "@angular/common";
import {Observable} from "rxjs";
import {AUTH_SERVICE, IAuthService} from "../../services/interfaces/auth-service";

@Component({
  selector: 'app-navbar',
    imports: [
        RouterLink,
        RouterLinkActive,
        NgClass,
        NgIf,
        AsyncPipe
    ],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.css'
})
export class NavbarComponent implements OnInit {
    menuCollapsed: boolean = true;
    isLoggedIn$!: Observable<boolean>;

    constructor(
        @Inject(AUTH_SERVICE) private authService: IAuthService,
        private router: Router) { }

    ngOnInit() {
        this.isLoggedIn$ = this.authService.authenticated;

        this.authService.authenticated.subscribe({
            next: (isLoggedIn: boolean) => {
                console.log('Is logged in:', isLoggedIn);
            },
            error: (err) => console.error('Error:', err)
        });
    }

    onLogout() {
        this.authService.logout();
        this.router.navigate(['logout']);
    }
}
