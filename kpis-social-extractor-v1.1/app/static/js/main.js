/**
 * KPIs Social Extractor - Main JavaScript
 * Handles form submission and API interactions for the home page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get form and result elements
    const extractionForm = document.getElementById('extractionForm');
    const loader = document.getElementById('loader');
    const resultsContainer = document.getElementById('resultsContainer');
    
    // Add form submission handler
    if (extractionForm) {
        extractionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show loader and hide previous results
            loader.style.display = 'block';
            resultsContainer.style.display = 'none';
            
            // Collect form data
            const formData = {
                websiteUrl: document.getElementById('websiteUrl').value,
                facebookUrl: document.getElementById('facebookUrl').value,
                instagramUrl: document.getElementById('instagramUrl').value,
                youtubeUrl: document.getElementById('youtubeUrl').value,
                linkedinUrl: document.getElementById('linkedinUrl').value,
                twitterUrl: document.getElementById('twitterUrl').value,
                tiktokUrl: document.getElementById('tiktokUrl').value
            };
            
            // Call API to extract KPIs
            extractKPIs(formData);
        });
    }
    
    /**
     * Extract KPIs from social media profiles
     * @param {Object} formData - Form data with social media URLs
     */
    async function extractKPIs(formData) {
        try {
            // Make a real API call to the backend
            const response = await fetch('/api/extract', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (!result.success) {
                throw new Error(result.message || 'Unknown error occurred');
            }
            
            // Store the data in sessionStorage for the dashboard
            sessionStorage.setItem('kpiData', JSON.stringify(result.data));
            
            // Display results on the current page
            displayResults(result.data);
            
            // Hide loader and show results
            loader.style.display = 'none';
            resultsContainer.style.display = 'block';
            
            // Scroll to results
            resultsContainer.scrollIntoView({ behavior: 'smooth' });
            
            // Add a button to view the dashboard with this data
            const dashboardButton = document.createElement('button');
            dashboardButton.className = 'btn btn-primary mt-4';
            dashboardButton.textContent = 'View Analytics Dashboard';
            dashboardButton.onclick = function() {
                window.location.href = '/dashboard';
            };
            
            // Add the button to the results container if it doesn't exist
            if (!document.getElementById('dashboardButton')) {
                dashboardButton.id = 'dashboardButton';
                resultsContainer.appendChild(dashboardButton);
            }
            
        } catch (error) {
            console.error('Error extracting KPIs:', error);
            alert('An error occurred while extracting KPIs: ' + error.message);
            loader.style.display = 'none';
        }
    }
    
    /**
     * Display results in the UI
     * @param {Object} data - KPI data to display
     */
    function displayResults(data) {
        // Website data
        if (data.website) {
            document.getElementById('websiteTitle').textContent = data.website.title;
            document.getElementById('websiteDescription').textContent = data.website.description;
        }
        
        // Facebook data
        if (data.facebook) {
            document.getElementById('facebookFollowers').textContent = formatNumber(data.facebook.followers);
            document.getElementById('facebookPosts').textContent = data.facebook.posts;
            document.getElementById('facebookLikes').textContent = data.facebook.avgLikes;
            document.getElementById('facebookComments').textContent = data.facebook.avgComments;
            document.getElementById('facebookEngagement').textContent = data.facebook.totalEngagement;
        }
        
        // Instagram data
        if (data.instagram) {
            document.getElementById('instagramFollowers').textContent = formatNumber(data.instagram.followers);
            document.getElementById('instagramPosts').textContent = data.instagram.posts;
            document.getElementById('instagramLikes').textContent = data.instagram.avgLikes;
            document.getElementById('instagramComments').textContent = data.instagram.avgComments;
            document.getElementById('instagramEngagement').textContent = data.instagram.totalEngagement;
        }
        
        // YouTube data
        if (data.youtube) {
            document.getElementById('youtubeSubscribers').textContent = formatNumber(data.youtube.subscribers);
            document.getElementById('youtubeVideos').textContent = data.youtube.videos;
            document.getElementById('youtubeViews').textContent = formatNumber(data.youtube.avgViews);
            document.getElementById('youtubeLikes').textContent = data.youtube.avgLikes;
            document.getElementById('youtubeComments').textContent = data.youtube.avgComments;
        }
        
        // LinkedIn data
        if (data.linkedin) {
            document.getElementById('linkedinFollowers').textContent = formatNumber(data.linkedin.followers);
            document.getElementById('linkedinPosts').textContent = data.linkedin.posts;
            document.getElementById('linkedinLikes').textContent = data.linkedin.avgLikes;
            document.getElementById('linkedinComments').textContent = data.linkedin.avgComments;
            document.getElementById('linkedinEngagement').textContent = data.linkedin.totalEngagement;
        }
        
        // Twitter data
        if (data.twitter) {
            document.getElementById('twitterFollowers').textContent = formatNumber(data.twitter.followers);
            document.getElementById('twitterTweets').textContent = data.twitter.tweets;
            document.getElementById('twitterLikes').textContent = data.twitter.avgLikes;
            document.getElementById('twitterRetweets').textContent = data.twitter.avgRetweets;
            document.getElementById('twitterEngagement').textContent = data.twitter.totalEngagement;
        }
        
        // TikTok data
        if (data.tiktok) {
            document.getElementById('tiktokFollowers').textContent = formatNumber(data.tiktok.followers);
            document.getElementById('tiktokVideos').textContent = data.tiktok.videos;
            document.getElementById('tiktokLikes').textContent = formatNumber(data.tiktok.avgLikes);
            document.getElementById('tiktokComments').textContent = data.tiktok.avgComments;
            document.getElementById('tiktokShares').textContent = data.tiktok.avgShares;
        }
    }
    
    /**
     * Format number with K/M suffix for readability
     * @param {number} num - Number to format
     * @returns {string} - Formatted number
     */
    function formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        }
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }
});
