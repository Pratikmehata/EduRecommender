class EduRecommender {
    constructor() {
        this.initEventListeners();
        this.loadAnalyticsSummary();
        this.loadModelInfo();
    }

    initEventListeners() {
        document.getElementById('recommendation-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.getRecommendations();
        });

        document.getElementById('export-pdf').addEventListener('click', () => {
            this.exportToPDF();
        });

        document.getElementById('train-model').addEventListener('click', () => {
            this.trainModel();
        });
    }

    async loadModelInfo() {
        try {
            const response = await fetch('/api/predictions/model_info');
            const result = await response.json();
            
            if (result.success) {
                const modelInfoElement = document.getElementById('model-info');
                modelInfoElement.innerHTML = `
                    <p class="text-sm"><strong>Model Type:</strong> ${result.model_info.model_type}</p>
                    <p class="text-sm"><strong>Classes:</strong> ${result.model_info.n_classes}</p>
                `;
            }
        } catch (error) {
            console.error('Failed to load model info:', error);
        }
    }

    async getRecommendations() {
        const formData = new FormData(document.getElementById('recommendation-form'));
        const userData = {
            math_score: parseInt(formData.get('math_score')),
            science_score: parseInt(formData.get('science_score')),
            reading_score: parseInt(formData.get('reading_score')),
            learning_style: parseInt(formData.get('learning_style')),
            interest_level: parseInt(formData.get('interest_level')),
            previous_performance: parseInt(formData.get('previous_performance'))
        };

        try {
            this.showLoading();
            const response = await fetch('/api/predictions/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            const result = await response.json();

            if (result.success) {
                this.displayRecommendations(result.recommendations, result.predicted_categories, result.probabilities);
                this.trackAnalytics(userData, result);
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            this.showError('Network error: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    displayRecommendations(recommendations, categories, probabilities) {
        const container = document.getElementById('recommendations-container');
        container.innerHTML = '';

        // Display predicted categories with confidence scores
        const categoryElement = document.createElement('div');
        categoryElement.className = 'mb-6 p-4 bg-blue-50 rounded-lg';
        
        let categoriesHtml = '<h3 class="text-lg font-semibold mb-2">Predicted Learning Categories:</h3><div class="flex flex-wrap gap-2">';
        
        categories.forEach((category, index) => {
            const confidence = (probabilities[index] * 100).toFixed(1);
            categoriesHtml += `
                <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                    ${category} (${confidence}%)
                </span>
            `;
        });
        
        categoriesHtml += '</div>';
        categoryElement.innerHTML = categoriesHtml;
        container.appendChild(categoryElement);

        // Display recommendations
        const recommendationsElement = document.createElement('div');
        recommendationsElement.innerHTML = '<h3 class="text-lg font-semibold mb-4">Recommended Learning Materials:</h3>';
        
        recommendations.forEach((rec, index) => {
            const confidence = (rec.confidence * 100).toFixed(1);
            const card = this.createRecommendationCard(rec, index + 1, confidence);
            recommendationsElement.appendChild(card);
        });

        container.appendChild(recommendationsElement);
        container.classList.remove('hidden');
        document.getElementById('no-recommendations').classList.add('hidden');
    }

    createRecommendationCard(recommendation, index, confidence) {
        const card = document.createElement('div');
        card.className = 'bg-white p-4 rounded-lg shadow-md mb-4 recommendation-card';
        
        // Get appropriate icon based on type
        let icon = '📚';
        if (recommendation.type === 'course') icon = '🎓';
        if (recommendation.type === 'activity') icon = '🔬';
        
        card.innerHTML = `
            <div class="flex items-start justify-between">
                <div class="flex-1">
                    <div class="flex items-center mb-2">
                        <span class="text-xl mr-2">${icon}</span>
                        <h4 class="font-semibold text-lg text-gray-800">${index}. ${recommendation.title}</h4>
                    </div>
                    <div class="grid grid-cols-2 gap-2 text-sm text-gray-600">
                        <div>
                            <span class="font-medium">Type:</span> 
                            <span class="capitalize">${recommendation.type}</span>
                        </div>
                        <div>
                            <span class="font-medium">Difficulty:</span> 
                            <span class="capitalize">${recommendation.difficulty}</span>
                        </div>
                        <div>
                            <span class="font-medium">Category:</span> 
                            <span>${recommendation.category}</span>
                        </div>
                        <div>
                            <span class="font-medium">Confidence:</span> 
                            <span>${confidence}%</span>
                        </div>
                    </div>
                    ${recommendation.duration ? `<div class="mt-2"><span class="font-medium">Duration:</span> ${recommendation.duration}</div>` : ''}
                    ${recommendation.pages ? `<div><span class="font-medium">Pages:</span> ${recommendation.pages}</div>` : ''}
                    ${recommendation.time_required ? `<div><span class="font-medium">Time Required:</span> ${recommendation.time_required}</div>` : ''}
                </div>
            </div>
        `;
        
        return card;
    }

    async trainModel() {
        try {
            this.showLoading();
            const response = await fetch('/api/predictions/train_model', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                alert('Model trained successfully! Accuracy: ' + result.accuracy);
                this.loadModelInfo(); // Reload model info
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            this.showError('Training error: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    async trackAnalytics(userData, recommendationResult) {
        try {
            await fetch('/api/analytics/track', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    event_type: 'recommendation_generated',
                    user_data: userData,
                    recommendation_data: {
                        categories: recommendationResult.predicted_categories,
                        probabilities: recommendationResult.probabilities,
                        count: recommendationResult.recommendations.length
                    }
                })
            });
        } catch (error) {
            console.error('Analytics tracking failed:', error);
        }
    }

    async loadAnalyticsSummary() {
        try {
            const response = await fetch('/api/analytics/summary');
            const result = await response.json();
            
            if (result.success) {
                this.updateAnalyticsDashboard(result.summary);
            }
        } catch (error) {
            console.error('Failed to load analytics:', error);
        }
    }

    updateAnalyticsDashboard(summary) {
        const analyticsElement = document.getElementById('analytics-summary');
        if (analyticsElement) {
            analyticsElement.innerHTML = `
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="bg-white p-4 rounded-lg shadow">
                        <h4 class="font-semibold">Total Recommendations</h4>
                        <p class="text-2xl font-bold text-blue-600">${summary.total_recommendations}</p>
                    </div>
                    <div class="bg-white p-4 rounded-lg shadow">
                        <h4 class="font-semibold">Popular Categories</h4>
                        ${Object.entries(summary.popular_categories || {}).map(([cat, count]) => 
                            `<p class="text-sm">${cat}: ${count}</p>`
                        ).join('')}
                    </div>
                    <div class="bg-white p-4 rounded-lg shadow">
                        <h4 class="font-semibold">Time Analysis</h4>
                        ${Object.entries(summary.time_based_analysis || {}).map(([time, count]) => 
                            `<p class="text-sm">${time}: ${count}</p>`
                        ).join('')}
                    </div>
                </div>
            `;
        }
    }

    exportToPDF() {
        // This would integrate with pdf.js
        const recommendations = document.getElementById('recommendations-container').innerHTML;
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>Educational Recommendations</title>
                    <style>
                        body { font-family: Arial, sans-serif; padding: 20px; }
                        .recommendation { margin-bottom: 15px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
                    </style>
                </head>
                <body>
                    <h1>Educational Recommendations</h1>
                    <div>${recommendations}</div>
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }

    showLoading() {
        document.getElementById('loading').classList.remove('hidden');
    }

    hideLoading() {
        document.getElementById('loading').classList.add('hidden');
    }

    showError(message) {
        const errorDiv = document.getElementById('error-message');
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
        setTimeout(() => errorDiv.classList.add('hidden'), 5000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new EduRecommender();
});