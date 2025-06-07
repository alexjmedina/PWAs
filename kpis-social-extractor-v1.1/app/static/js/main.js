/**
 * KPIs Social Extractor - Main JavaScript
 * Handles form submission and API interactions for the home page
 */
document.addEventListener('DOMContentLoaded', function() {
    const extractionForm = document.getElementById('extractionForm');
    const loader = document.getElementById('loader');
    const resultsContainer = document.getElementById('resultsContainer');

    if (extractionForm) {
        extractionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            loader.style.display = 'block';
            resultsContainer.style.display = 'none';

            const formData = {
                websiteUrl: document.getElementById('websiteUrl').value,
                facebookUrl: document.getElementById('facebookUrl').value,
                instagramUrl: document.getElementById('instagramUrl').value,
                youtubeUrl: document.getElementById('youtubeUrl').value,
                linkedinUrl: document.getElementById('linkedinUrl').value,
                twitterUrl: document.getElementById('twitterUrl').value,
                tiktokUrl: document.getElementById('tiktokUrl').value
            };
            extractKPIs(formData);
        });
    }

    async function extractKPIs(formData) {
        try {
            const response = await fetch('/api/extract', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const result = await response.json();
            if (!result.success) {
                throw new Error(result.message || 'An unknown error occurred on the server.');
            }

            sessionStorage.setItem('kpiData', JSON.stringify(result.data));
            displayResults(result.data);

        } catch (error) {
            console.error('Error extracting KPIs:', error);
            alert('An error occurred while extracting KPIs: ' + error.message);
        } finally {
            loader.style.display = 'none';
            resultsContainer.style.display = 'block';
            resultsContainer.scrollIntoView({ behavior: 'smooth' });
        }
    }

    function displayResults(data) {
        // Helper function to safely update text content
        const updateText = (elementId, value, formatter = (v) => v) => {
            const element = document.getElementById(elementId);
            if (element) {
                element.textContent = value !== null && value !== undefined ? formatter(value) : '-';
            }
        };

        // Website data
        if (data.website) {
            updateText('websiteTitle', data.website.title);
            updateText('websiteDescription', data.website.description);
        }

        // Facebook data
        if (data.facebook) {
            updateText('facebookFollowers', data.facebook.followers, formatNumber);
            updateText('facebookPosts', data.facebook.posts);
            updateText('facebookLikes', data.facebook.avgLikes);
            updateText('facebookComments', data.facebook.avgComments);
            updateText('facebookEngagement', data.facebook.totalEngagement);
        }

        // Instagram data
        if (data.instagram) {
            updateText('instagramFollowers', data.instagram.followers, formatNumber);
            updateText('instagramPosts', data.instagram.posts);
            updateText('instagramLikes', data.instagram.avgLikes);
            updateText('instagramComments', data.instagram.avgComments);
            updateText('instagramEngagement', data.instagram.totalEngagement);
        }

        // YouTube data
        if (data.youtube) {
            updateText('youtubeSubscribers', data.youtube.subscribers, formatNumber);
            updateText('youtubeVideos', data.youtube.videos);
            updateText('youtubeViews', data.youtube.avgViews, formatNumber);
            updateText('youtubeLikes', data.youtube.avgLikes, formatNumber);
            updateText('youtubeComments', data.youtube.avgComments, formatNumber);
        }

        // LinkedIn data
        if (data.linkedin) {
            updateText('linkedinFollowers', data.linkedin.followers, formatNumber);
            updateText('linkedinPosts', data.linkedin.posts);
            updateText('linkedinLikes', data.linkedin.avgLikes);
            updateText('linkedinComments', data.linkedin.avgComments);
            updateText('linkedinEngagement', data.linkedin.totalEngagement);
        }

        // Twitter data
        if (data.twitter) {
            updateText('twitterFollowers', data.twitter.followers, formatNumber);
            updateText('twitterTweets', data.twitter.tweets);
            updateText('twitterLikes', data.twitter.avgLikes);
            updateText('twitterRetweets', data.twitter.avgRetweets);
            updateText('twitterEngagement', data.twitter.totalEngagement);
        }

        // TikTok data
        if (data.tiktok) {
            updateText('tiktokFollowers', data.tiktok.followers, formatNumber);
            updateText('tiktokVideos', data.tiktok.videos);
            updateText('tiktokLikes', data.tiktok.avgLikes, formatNumber);
            updateText('tiktokComments', data.tiktok.avgComments, formatNumber);
            updateText('tiktokShares', data.tiktok.avgShares);
        }
    }

    function formatNumber(num) {
        if (num === null || num === undefined) return '-';
        if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
        return num.toString();
    }
});