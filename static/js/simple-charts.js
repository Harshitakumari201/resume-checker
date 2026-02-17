// Simple chart library for Resume Checker
const SimpleCharts = {
    // Draw a gauge chart
    drawGauge: function(canvasId, value, title) {
        const canvas = document.getElementById(canvasId);
        const ctx = canvas.getContext('2d');
        canvas.width = 300;
        canvas.height = 200;
        
        const centerX = canvas.width / 2;
        const centerY = canvas.height - 20;
        const radius = 80;
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw background arc
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, Math.PI, 2 * Math.PI);
        ctx.lineWidth = 20;
        ctx.strokeStyle = '#e9ecef';
        ctx.stroke();
        
        // Draw value arc
        const endAngle = Math.PI + (value / 100) * Math.PI;
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, Math.PI, endAngle);
        ctx.lineWidth = 20;
        ctx.strokeStyle = value >= 70 ? '#28a745' : value >= 50 ? '#ffc107' : '#dc3545';
        ctx.stroke();
        
        // Draw title
        ctx.font = 'bold 16px Arial';
        ctx.fillStyle = '#333';
        ctx.textAlign = 'center';
        ctx.fillText(title, centerX, 30);
        
        // Draw value
        ctx.font = 'bold 36px Arial';
        ctx.fillText(value, centerX, centerY - 10);
    },
    
    // Draw a bar chart
    drawBar: function(canvasId, labels, values, title) {
        const canvas = document.getElementById(canvasId);
        const ctx = canvas.getContext('2d');
        canvas.width = 350;
        canvas.height = 250;
        
        const padding = 40;
        const chartWidth = canvas.width - 2 * padding;
        const chartHeight = canvas.height - 2 * padding - 30;
        const barWidth = chartWidth / labels.length - 10;
        const maxValue = 100;
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw title
        ctx.font = 'bold 14px Arial';
        ctx.fillStyle = '#333';
        ctx.textAlign = 'center';
        ctx.fillText(title, canvas.width / 2, 20);
        
        // Draw bars
        const colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe'];
        labels.forEach((label, i) => {
            const barHeight = (values[i] / maxValue) * chartHeight;
            const x = padding + i * (barWidth + 10);
            const y = canvas.height - padding - barHeight;
            
            // Draw bar
            ctx.fillStyle = colors[i % colors.length];
            ctx.fillRect(x, y, barWidth, barHeight);
            
            // Draw value on top
            ctx.fillStyle = '#333';
            ctx.font = 'bold 12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(values[i] + '%', x + barWidth / 2, y - 5);
            
            // Draw label
            ctx.save();
            ctx.translate(x + barWidth / 2, canvas.height - padding + 10);
            ctx.rotate(-Math.PI / 4);
            ctx.font = '10px Arial';
            ctx.textAlign = 'right';
            ctx.fillText(label.substring(0, 15), 0, 0);
            ctx.restore();
        });
    },
    
    // Draw a pie chart
    drawPie: function(canvasId, labels, values, title) {
        const canvas = document.getElementById(canvasId);
        const ctx = canvas.getContext('2d');
        canvas.width = 350;
        canvas.height = 280;
        
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2 - 10;
        const radius = 80;
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw title
        ctx.font = 'bold 14px Arial';
        ctx.fillStyle = '#333';
        ctx.textAlign = 'center';
        ctx.fillText(title, centerX, 20);
        
        const total = values.reduce((a, b) => a + b, 0);
        if (total === 0) return;
        
        let currentAngle = -Math.PI / 2;
        const colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe'];
        
        // Draw slices
        values.forEach((value, i) => {
            const sliceAngle = (value / total) * 2 * Math.PI;
            
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
            ctx.closePath();
            ctx.fillStyle = colors[i % colors.length];
            ctx.fill();
            
            // Draw percentage if significant
            if (value / total > 0.05) {
                const textAngle = currentAngle + sliceAngle / 2;
                const textX = centerX + Math.cos(textAngle) * radius * 0.6;
                const textY = centerY + Math.sin(textAngle) * radius * 0.6;
                ctx.fillStyle = '#fff';
                ctx.font = 'bold 12px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(Math.round((value / total) * 100) + '%', textX, textY);
            }
            
            currentAngle += sliceAngle;
        });
        
        // Draw legend
        const legendY = canvas.height - 60;
        labels.forEach((label, i) => {
            const x = 20 + (i % 2) * 170;
            const y = legendY + Math.floor(i / 2) * 20;
            
            // Color box
            ctx.fillStyle = colors[i % colors.length];
            ctx.fillRect(x, y, 12, 12);
            
            // Label
            ctx.fillStyle = '#333';
            ctx.font = '11px Arial';
            ctx.textAlign = 'left';
            ctx.fillText(label.substring(0, 20), x + 18, y + 10);
        });
    }
};
