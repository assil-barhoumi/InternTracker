django.jQuery(function($) {
    console.log('Internship offer admin script loaded');
    
    function calculateEndDate() {
        const startDate = $('#id_start_date').val();
        const duration = $('#id_duration').val();
        const endDateField = $('#id_end_date');
        
        console.log('Calculating end date:', { startDate, duration });
        
        if (startDate && duration) {
            try {
                const durationParts = duration.toLowerCase().split();
                if (durationParts.length >= 2) {
                    const amount = parseInt(durationParts[0]);
                    const unit = durationParts[1];
                    
                    console.log('Parsed duration:', { amount, unit });
                    
                    const start = new Date(startDate);
                    let endDate = new Date(start);
                    
                    if (unit.includes('month')) {
                        endDate.setMonth(endDate.getMonth() + amount);
                    } else if (unit.includes('year')) {
                        endDate.setFullYear(endDate.getFullYear() + amount);
                    } else {
                        console.log('Invalid unit:', unit);
                        return;
                    }
                    
                    const formattedDate = endDate.toISOString().split('T')[0];
                    console.log('Setting end date to:', formattedDate);
                    endDateField.val(formattedDate);
                    
                    endDateField.css('background-color', '#e8f5e8');
                    setTimeout(() => {
                        endDateField.css('background-color', '');
                    }, 1000);
                } else {
                    console.log('Duration parts insufficient:', durationParts);
                }
            } catch (e) {
                console.error('Error calculating end date:', e);
            }
        } else {
            console.log('Missing start date or duration');
        }
    }
    
    function validateStartDate() {
        const startDate = $('#id_start_date').val();
        if (startDate) {
            const selectedDate = new Date(startDate);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            selectedDate.setHours(0, 0, 0, 0);
            
            if (selectedDate < today) {
                alert('Start date cannot be in the past. Please select a date today or in the future.');
                $('#id_start_date').val('');
                return false;
            }
        }
        return true;
    }
    
    $('#id_start_date').on('change', function() {
        console.log('Start date changed');
        if (validateStartDate()) {
            calculateEndDate();
        }
    });
    
    $('#id_duration').on('input', function() {
        console.log('Duration changed');
        calculateEndDate();
    });
    calculateEndDate();
});
