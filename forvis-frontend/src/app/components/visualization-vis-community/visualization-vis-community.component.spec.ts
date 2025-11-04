import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { VisualizationVisCommunityComponent } from './visualization-vis-community.component';

describe('VisualizationVisCommunityComponent', () => {
  let component: VisualizationVisCommunityComponent;
  let fixture: ComponentFixture<VisualizationVisCommunityComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ VisualizationVisCommunityComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(VisualizationVisCommunityComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
