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
            // In a real app, this would be an API call
            // For demo purposes, we'll simulate a delay and use mock data
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Mock data for demonstration
            const mockData = generateMockData(formData);
            
            // Display results
            displayResults(mockData);
            
            // Hide loader and show results
            loader.style.display = 'none';
            resultsContainer.style.display = 'block';
            
            // Scroll to results
            resultsContainer.scrollIntoView({ behavior: 'smooth' });
            
        } catch (error) {
            console.error('Error extracting KPIs:', error);
            alert('An error occurred while extracting KPIs. Please try again.');
            loader.style.display = 'none';
        }
    }
    
    /**
     * Generate mock data for demonstration
     * @param {Object} formData - Form data with social media URLs
     * @returns {Object} - Mock data for demonstration
     */
    function generateMockData(formData) {
        // Extract domain from website URL for title
        let websiteTitle = 'Unknown Website';
        let websiteDescription = 'No description available';
        
        if (formData.websiteUrl) {
            try {
                const url = new URL(formData.websiteUrl);
                websiteTitle = url.hostname.replace('www.', '').split('.')[0];
                websiteTitle = websiteTitle.charAt(0).toUpperCase() + websiteTitle.slice(1);
                
                if (websiteTitle.toLowerCase().includes('aden')) {
                    websiteTitle = 'ADEN International Business School | Escuela de Negocios';
                    websiteDescription = 'Escuela de Negocios abocada al desarrollo profesional de Directivos y Gerentes. ADEN tiene 20 sedes en América Latina. Business School.';
                }
            } catch (e) {
                console.error('Invalid URL:', e);
            }
        }
        
        return {
            website: {
                title: websiteTitle,
                description: websiteDescription
            },
            facebook: formData.facebookUrl ? {
                followers: Math.floor(Math.random() * 10000) + 5000,
                posts: Math.floor(Math.random() * 10) + 1,
                avgLikes: Math.floor(Math.random() * 100) + 10,
                avgComments: Math.floor(Math.random() * 20) + 1,
                totalEngagement: Math.floor(Math.random() * 120) + 11
            } : null,
            instagram: formData.instagramUrl ? {
                followers: Math.floor(Math.random() * 20000) + 10000,
                posts: Math.floor(Math.random() * 20) + 5,
                avgLikes: Math.floor(Math.random() * 500) + 100,
                avgComments: Math.floor(Math.random() * 50) + 5,
                totalEngagement: Math.floor(Math.random() * 550) + 105
            } : null,
            youtube: formData.youtubeUrl ? {
                subscribers: Math.floor(Math.random() * 50000) + 1000,
                videos: Math.floor(Math.random() * 50) + 10,
                avgViews: Math.floor(Math.random() * 5000) + 500,
                avgLikes: Math.floor(Math.random() * 200) + 50,
                avgComments: Math.floor(Math.random() * 50) + 10
            } : null,
            linkedin: formData.linkedinUrl ? {
                followers: Math.floor(Math.random() * 5000) + 1000,
                posts: Math.floor(Math.random() * 15) + 5,
                avgLikes: Math.floor(Math.random() * 50) + 10,
                avgComments: Math.floor(Math.random() * 10) + 1,
                totalEngagement: Math.floor(Math.random() * 60) + 11
            } : null,
            twitter: formData.twitterUrl ? {
                followers: Math.floor(Math.random() * 10000) + 1000,
                tweets: Math.floor(Math.random() * 100) + 10,
                avgLikes: Math.floor(Math.random() * 30) + 5,
                avgRetweets: Math.floor(Math.random() * 10) + 1,
                avgReplies: Math.floor(Math.random() * 5) + 1,
                totalEngagement: Math.floor(Math.random() * 45) + 7
            } : null,
            tiktok: formData.tiktokUrl ? {
                followers: Math.floor(Math.random() * 50000) + 5000,
                videos: Math.floor(Math.random() * 30) + 5,
                avgViews: Math.floor(Math.random() * 10000) + 1000,
                avgLikes: Math.floor(Math.random() * 1000) + 100,
                avgComments: Math.floor(Math.random() * 100) + 10,
                avgShares: Math.floor(Math.random() * 50) + 5
            } : null
        };
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
