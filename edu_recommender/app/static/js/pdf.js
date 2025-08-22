class PDFExporter {
    constructor() {
        this.loadPDFLibraries();
    }

    loadPDFLibraries() {
        // Load jsPDF library
        if (typeof window.jspdf === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
            script.onload = () => {
                this.loadHtml2Canvas();
            };
            document.head.appendChild(script);
        } else {
            this.loadHtml2Canvas();
        }
    }

    loadHtml2Canvas() {
        // Load html2canvas library
        if (typeof window.html2canvas === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
            script.onload = () => {
                console.log('PDF libraries loaded successfully');
            };
            document.head.appendChild(script);
        } else {
            console.log('PDF libraries already loaded');
        }
    }

    async exportToPDF() {
        // Check if libraries are loaded
        if (typeof window.jspdf === 'undefined' || typeof window.html2canvas === 'undefined') {
            alert('PDF libraries are still loading. Please try again in a moment.');
            return;
        }

        try {
            // Show loading indicator
            this.showPDFLoading(true);

            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            
            // Get student data from form
            const studentData = this.getStudentData();
            
            // Add header with student information
            this.addHeader(doc, studentData);
            
            // Add recommendations section
            await this.addRecommendations(doc);
            
            // Add analytics section (if available)
            await this.addAnalytics(doc);
            
            // Add footer with timestamp
            this.addFooter(doc);
            
            // Save the PDF
            const fileName = `Educational_Recommendations_${new Date().toISOString().split('T')[0]}.pdf`;
            doc.save(fileName);
            
            // Track PDF export event
            this.trackPDFExport(studentData);
            
        } catch (error) {
            console.error('PDF export error:', error);
            alert('Error generating PDF: ' + error.message);
        } finally {
            // Hide loading indicator
            this.showPDFLoading(false);
        }
    }

    getStudentData() {
        const form = document.getElementById('recommendation-form');
        if (!form) return {};
        
        return {
            mathScore: form.querySelector('[name="math_score"]').value,
            scienceScore: form.querySelector('[name="science_score"]').value,
            readingScore: form.querySelector('[name="reading_score"]').value,
            learningStyle: this.getLearningStyleText(form.querySelector('[name="learning_style"]').value),
            interestLevel: this.getInterestLevelText(form.querySelector('[name="interest_level"]').value),
            performance: this.getPerformanceText(form.querySelector('[name="previous_performance"]').value)
        };
    }

    getLearningStyleText(value) {
        const styles = {
            '0': 'Visual Learner',
            '1': 'Auditory Learner',
            '2': 'Kinesthetic Learner'
        };
        return styles[value] || 'Not specified';
    }

    getInterestLevelText(value) {
        const levels = {
            '0': 'Low Interest',
            '1': 'Medium Interest',
            '2': 'High Interest'
        };
        return levels[value] || 'Not specified';
    }

    getPerformanceText(value) {
        const levels = {
            '0': 'Below Average',
            '1': 'Average',
            '2': 'Above Average'
        };
        return levels[value] || 'Not specified';
    }

    addHeader(doc, studentData) {
        // Title
        doc.setFontSize(20);
        doc.setTextColor(40, 40, 40);
        doc.text('Educational Recommendations Report', 105, 20, { align: 'center' });
        
        // Student information
        doc.setFontSize(12);
        doc.setTextColor(100, 100, 100);
        doc.text(`Generated on: ${new Date().toLocaleDateString()}`, 105, 30, { align: 'center' });
        
        // Add a line
        doc.setDrawColor(200, 200, 200);
        doc.line(20, 35, 190, 35);
        
        // Student data section
        doc.setFontSize(14);
        doc.setTextColor(40, 40, 40);
        doc.text('Student Profile', 20, 45);
        
        doc.setFontSize(10);
        doc.setTextColor(80, 80, 80);
        doc.text(`Math Score: ${studentData.mathScore}`, 20, 55);
        doc.text(`Science Score: ${studentData.scienceScore}`, 20, 60);
        doc.text(`Reading Score: ${studentData.readingScore}`, 20, 65);
        doc.text(`Learning Style: ${studentData.learningStyle}`, 20, 70);
        doc.text(`Interest Level: ${studentData.interestLevel}`, 20, 75);
        doc.text(`Previous Performance: ${studentData.performance}`, 20, 80);
        
        // Add another line
        doc.line(20, 85, 190, 85);
    }

    async addRecommendations(doc) {
        const recommendationsContainer = document.getElementById('recommendations-container');
        if (!recommendationsContainer || recommendationsContainer.classList.contains('hidden')) {
            doc.setFontSize(12);
            doc.setTextColor(150, 150, 150);
            doc.text('No recommendations available. Please generate recommendations first.', 20, 95);
            return;
        }
        
        // Add recommendations title
        doc.setFontSize(14);
        doc.setTextColor(40, 40, 40);
        doc.text('Learning Recommendations', 20, 95);
        
        // Capture the recommendations as an image
        try {
            const canvas = await html2canvas(recommendationsContainer, {
                scale: 2,
                useCORS: true,
                logging: false
            });
            
            const imgData = canvas.toDataURL('image/jpeg', 0.8);
            
            // Calculate dimensions to fit in PDF
            const imgWidth = 170;
            const pageHeight = 280;
            const imgHeight = (canvas.height * imgWidth) / canvas.width;
            
            // Add the image to PDF
            doc.addImage(imgData, 'JPEG', 20, 100, imgWidth, imgHeight);
            
            // Add new page if content is too long
            if (100 + imgHeight > pageHeight) {
                doc.addPage();
            }
            
        } catch (error) {
            console.error('Error capturing recommendations:', error);
            doc.setFontSize(10);
            doc.setTextColor(150, 150, 150);
            doc.text('Could not capture recommendations visually. Please try again.', 20, 100);
        }
    }

    async addAnalytics(doc) {
        const analyticsElement = document.getElementById('analytics-summary');
        if (!analyticsElement || analyticsElement.textContent.includes('Loading analytics data')) {
            return; // Skip if no analytics available
        }
        
        // Add a new page for analytics
        doc.addPage();
        
        // Add analytics title
        doc.setFontSize(14);
        doc.setTextColor(40, 40, 40);
        doc.text('Learning Analytics Summary', 20, 20);
        
        // Capture analytics as image
        try {
            const canvas = await html2canvas(analyticsElement, {
                scale: 2,
                useCORS: true,
                logging: false
            });
            
            const imgData = canvas.toDataURL('image/jpeg', 0.8);
            
            // Calculate dimensions to fit in PDF
            const imgWidth = 170;
            const imgHeight = (canvas.height * imgWidth) / canvas.width;
            
            // Add the image to PDF
            doc.addImage(imgData, 'JPEG', 20, 30, imgWidth, imgHeight);
            
        } catch (error) {
            console.error('Error capturing analytics:', error);
            doc.setFontSize(10);
            doc.setTextColor(150, 150, 150);
            doc.text('Could not capture analytics data.', 20, 30);
        }
    }

    addFooter(doc) {
        const pageCount = doc.internal.getNumberOfPages();
        
        for (let i = 1; i <= pageCount; i++) {
            doc.setPage(i);
            
            // Footer text
            doc.setFontSize(8);
            doc.setTextColor(150, 150, 150);
            doc.text(`Page ${i} of ${pageCount}`, 105, 280, { align: 'center' });
            doc.text('Generated by Educational Recommender System', 105, 285, { align: 'center' });
        }
    }

    showPDFLoading(show) {
        let loadingIndicator = document.getElementById('pdf-loading');
        
        if (!loadingIndicator) {
            loadingIndicator = document.createElement('div');
            loadingIndicator.id = 'pdf-loading';
            loadingIndicator.innerHTML = `
                <div style="
                    position: fixed;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    z-index: 1000;
                    text-align: center;
                ">
                    <div class="loading-spinner" style="
                        border: 3px solid #f3f3f3;
                        border-top: 3px solid #3498db;
                        border-radius: 50%;
                        width: 30px;
                        height: 30px;
                        animation: spin 1s linear infinite;
                        margin: 0 auto 15px;
                    "></div>
                    <p>Generating PDF...</p>
                </div>
                <div style="
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.5);
                    z-index: 999;
                "></div>
            `;
            document.body.appendChild(loadingIndicator);
            
            // Add spin animation
            const style = document.createElement('style');
            style.textContent = `
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        }
        
        loadingIndicator.style.display = show ? 'block' : 'none';
    }

    trackPDFExport(studentData) {
        // Send analytics event to server
        fetch('/api/analytics/track', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                event_type: 'pdf_export',
                user_data: studentData,
                timestamp: new Date().toISOString()
            })
        }).catch(error => {
            console.error('Failed to track PDF export:', error);
        });
    }
}

// Initialize PDF exporter when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.pdfExporter = new PDFExporter();
    
    // Add event listener to PDF export button
    const exportButton = document.getElementById('export-pdf');
    if (exportButton) {
        exportButton.addEventListener('click', () => {
            window.pdfExporter.exportToPDF();
        });
    }
});