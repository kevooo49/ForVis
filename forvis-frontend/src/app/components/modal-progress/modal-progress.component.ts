import {Component, Input, OnInit} from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-modal-progress',
  imports: [],
  templateUrl: './modal-progress.component.html',
  styleUrl: './modal-progress.component.css'
})
export class ModalProgressComponent implements OnInit {
  @Input()
  progressMessage!: string;

  constructor(public activeModal: NgbActiveModal) {}

  ngOnInit() {
  }
}
