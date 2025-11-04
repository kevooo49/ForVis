import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-cnf-uploader',
  imports: [
    CommonModule
  ],
  template: `
    <div class="container">
      <div class="header">
        <h1 class="title">Choose your problem type</h1>
        <p class="subtitle">Select the type of satisfiability problem you want to solve</p>
      </div>

      <div class="cards-container">
        <div class="card" (click)="navigateToSat()">
          <div class="card-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 12l2 2 4-4"/>
              <circle cx="12" cy="12" r="10"/>
            </svg>
          </div>
          <h2 class="card-title">SAT</h2>
          <p class="card-description">
            <strong>Boolean Satisfiability Problem</strong><br>
            Determines if there exists an assignment of boolean variables that makes a given formula true.
            This is the classic NP-complete problem that asks: "Can this formula be satisfied?"
          </p>
          <div class="card-features">
            <span class="feature">• Decision Problem</span>
            <span class="feature">• True/False Answer</span>
            <span class="feature">• NP-Complete</span>
          </div>
          <button class="card-button primary">
            Solve SAT Problem
          </button>
        </div>

        <div class="card" (click)="navigateToMaxSat()">
          <div class="card-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
          </div>
          <h2 class="card-title">MaxSAT</h2>
          <p class="card-description">
            <strong>Maximum Satisfiability Problem</strong><br>
            Finds an assignment that satisfies the maximum number of clauses when the formula cannot be
            completely satisfied. This optimization variant asks: "What's the best we can do?"
          </p>
          <div class="card-features">
            <span class="feature">• Optimization Problem</span>
            <span class="feature">• Maximize Satisfied Clauses</span>
            <span class="feature">• NP-Hard</span>
          </div>
          <button class="card-button secondary">
            Solve MaxSAT Problem
          </button>
        </div>
      </div>

      <div class="info-section">
        <div class="info-card">
          <h3>💡 Quick Tip</h3>
          <p>If your formula might be unsatisfiable but you still want the best possible solution, choose <strong>MaxSAT</strong>.
            If you just need to know whether a complete solution exists, choose <strong>SAT</strong>.</p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .container {
      min-height: 100vh;
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 2rem;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .header {
      text-align: center;
      margin-bottom: 3rem;
    }

    .title {
      font-size: 2.5rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
    }

    .subtitle {
      font-size: 1.1rem;
      opacity: 0.9;
      margin: 0;
    }

    .cards-container {
      display: flex;
      gap: 2rem;
      margin-bottom: 2rem;
      flex-wrap: wrap;
      justify-content: center;
    }

    .card {
      background: white;
      border-radius: 1rem;
      padding: 2rem;
      width: 350px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.2);
      transition: all 0.3s ease;
      cursor: pointer;
      position: relative;
      overflow: hidden;
    }

    .card::before {
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
      transition: left 0.5s;
    }

    .card:hover {
      transform: translateY(-8px);
      box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    }

    .card:hover::before {
      left: 100%;
    }

    .card-icon {
      text-align: center;
      margin-bottom: 1rem;
      color: #667eea;
    }

    .card-title {
      font-size: 1.8rem;
      font-weight: 700;
      text-align: center;
      margin-bottom: 1rem;
      color: #2d3748;
    }

    .card-description {
      text-align: center;
      line-height: 1.6;
      margin-bottom: 1.5rem;
      color: #4a5568;
    }

    .card-features {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      margin-bottom: 1.5rem;
    }

    .feature {
      font-size: 0.9rem;
      color: #666;
      padding-left: 0.5rem;
    }

    .card-button {
      width: 100%;
      padding: 0.75rem 1.5rem;
      border: none;
      border-radius: 0.5rem;
      font-weight: 600;
      font-size: 1rem;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .primary {
      background: linear-gradient(135deg, #667eea, #764ba2);
      color: white;
    }

    .primary:hover {
      transform: scale(1.02);
      box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }

    .secondary {
      background: linear-gradient(135deg, #f093fb, #f5576c);
      color: white;
    }

    .secondary:hover {
      transform: scale(1.02);
      box-shadow: 0 5px 15px rgba(245, 87, 108, 0.4);
    }

    .info-section {
      max-width: 600px;
      width: 100%;
    }

    .info-card {
      background: rgba(255, 255, 255, 0.95);
      border-radius: 0.75rem;
      padding: 1.5rem;
      text-align: center;
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .info-card h3 {
      margin-bottom: 0.75rem;
      color: #2d3748;
      font-size: 1.1rem;
    }

    .info-card p {
      margin: 0;
      color: #4a5568;
      line-height: 1.5;
    }

    @media (max-width: 768px) {
      .cards-container {
        flex-direction: column;
        align-items: center;
      }

      .card {
        width: 100%;
        max-width: 350px;
      }

      .title {
        font-size: 2rem;
      }
    }
  `]
})
export class CnfUploader {

  constructor(private router: Router) {}

  navigateToMaxSat(): void {
    this.router.navigate(['/max-sat']);
  }

  navigateToSat(): void {
    this.router.navigate(['/sat']);
  }
}