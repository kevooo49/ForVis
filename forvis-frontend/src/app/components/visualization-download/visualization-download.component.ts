import { Network } from 'vis-network';
import jsPDF from 'jspdf';

export class DownloadableComponent {
  public network: Network | null = null;

  downloadPdf(): void {
    const dataUrl = this.getDataUrl();
    if (!dataUrl) {
      console.error('Unable to generate image for PDF.');
      return;
    }

    const pdf = new jsPDF('l', 'mm', 'a4');
    const width = pdf.internal.pageSize.getWidth();
    const height = pdf.internal.pageSize.getHeight();

    pdf.addImage(dataUrl, 'PNG', 0, 0, width, height);
    pdf.save('image.pdf');
  }

  downloadPng(): void {
    const dataUrl = this.getDataUrl();
    if (!dataUrl) {
      console.error('Unable to generate PNG.');
      return;
    }

    const anchor = document.createElement('a');
    anchor.download = 'image.png';
    anchor.href = dataUrl;
    anchor.click();
  }

  private getDataUrl(): string | null {
    const networkCanvas = (this.network as any)?.canvas?.frame?.canvas as HTMLCanvasElement | undefined;

    if (!networkCanvas) {
      console.error('Network canvas not initialized.');
      return null;
    }

    return networkCanvas.toDataURL('image/png');
  }
}