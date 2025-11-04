import {Component, Inject, OnInit} from '@angular/core';
import {ALERT_SERVICE, IAlertService} from "../../services/interfaces/alert-service";
import {NgClass} from "@angular/common";

@Component({
  selector: 'app-alert',
  imports: [
    NgClass
  ],
  templateUrl: './alert.component.html',
  styleUrl: './alert.component.css'
})
export class AlertComponent implements OnInit {
  message: any;

  constructor(
      @Inject(ALERT_SERVICE) private alertService: IAlertService) {
  }

  ngOnInit() {
    this.alertService.getMessage().subscribe({
      next: message => {
        this.message = message;
        setTimeout(() => {
          this.message = null;
        }, 1000 * 12)
      },
      error: err => {
        console.log('Failed to load message: ' + err);
      }
    });
  }
}
