/**
 * KPIs Social Extractor - Dashboard JavaScript
 * Handles chart creation and data visualization for the dashboard page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get KPI data from sessionStorage
    let kpiData = null;
    
    try {
        const storedData = sessionStorage.getItem('kpiData');
        if (storedData) {
            kpiData = JSON.parse(storedData);
            console.log('Retrieved KPI data from sessionStorage:', kpiData);
        } else {
            console.warn('No KPI data found in sessionStorage');
        }
    } catch (error) {
        console.error('Error retrieving KPI data from sessionStorage:', error);
    }
    
    // If no data is available, show a message and return
    if (!kpiData) {
        document.getElementById('dashboardContainer').innerHTML = `
            <div class="alert alert-warning" role="alert">
                <h4 class="alert-heading">No data available!</h4>
                <p>Please extract KPIs from the home page first.</p>
                <hr>
                <p class="mb-0">
                    <a href="/" class="btn btn-primary">Go to Home Page</a>
                </p>
            </div>
        `;
        return;
    }
    
    // Transform the data format to match what the dashboard functions expect
    const transformedData = transformKpiData(kpiData);
    
    // Create charts
    createFollowersChart(transformedData);
    createEngagementChart(transformedData);
    createPostFrequencyChart(transformedData);
    
    // Populate performance table
    populatePerformanceTable(transformedData);
    
    // Generate recommendations
    generateRecommendations(transformedData);
});

/**
 * Transform KPI data from API format to dashboard format
 * @param {Object} apiData - KPI data from API
 * @returns {Object} - Transformed data for dashboard
 */
function transformKpiData(apiData) {
    const result = {};
    
    // Transform Facebook data
    if (apiData.facebook) {
        result.facebook = {
            followers: apiData.facebook.followers || 0,
            engagement: {
                posts: apiData.facebook.posts || 0,
                avg_likes: apiData.facebook.avgLikes || 0,
                avg_comments: apiData.facebook.avgComments || 0,
                total_engagement: apiData.facebook.totalEngagement || 0
            }
        };
    }
    
    // Transform Instagram data
    if (apiData.instagram) {
        result.instagram = {
            followers: apiData.instagram.followers || 0,
            engagement: {
                posts: apiData.instagram.posts || 0,
                avg_likes: apiData.instagram.avgLikes || 0,
                avg_comments: apiData.instagram.avgComments || 0,
                total_engagement: apiData.instagram.totalEngagement || 0
            }
        };
    }
    
    // Transform YouTube data
    if (apiData.youtube) {
        result.youtube = {
            followers: apiData.youtube.subscribers || 0,
            engagement: {
                posts: apiData.youtube.videos || 0,
                avg_likes: apiData.youtube.avgLikes || 0,
                avg_comments: apiData.youtube.avgComments || 0,
                avg_views: apiData.youtube.avgViews || 0,
                total_engagement: apiData.youtube.avgLikes + apiData.youtube.avgComments || 0
            }
        };
    }
    
    // Transform LinkedIn data
    if (apiData.linkedin) {
        result.linkedin = {
            followers: apiData.linkedin.followers || 0,
            engagement: {
                posts: apiData.linkedin.posts || 0,
                avg_likes: apiData.linkedin.avgLikes || 0,
                avg_comments: apiData.linkedin.avgComments || 0,
                total_engagement: apiData.linkedin.totalEngagement || 0
            }
        };
    }
    
    // Transform Twitter data
    if (apiData.twitter) {
        result.twitter = {
            followers: apiData.twitter.followers || 0,
            engagement: {
                posts: apiData.twitter.tweets || 0,
                avg_likes: apiData.twitter.avgLikes || 0,
                avg_retweets: apiData.twitter.avgRetweets || 0,
                avg_replies: apiData.twitter.avgReplies || 0,
                total_engagement: apiData.twitter.totalEngagement || 0
            }
        };
    }
    
    // Transform TikTok data
    if (apiData.tiktok) {
        result.tiktok = {
            followers: apiData.tiktok.followers || 0,
            engagement: {
                posts: apiData.tiktok.videos || 0,
                avg_likes: apiData.tiktok.avgLikes || 0,
                avg_comments: apiData.tiktok.avgComments || 0,
                avg_shares: apiData.tiktok.avgShares || 0,
                total_engagement: apiData.tiktok.avgLikes + apiData.tiktok.avgComments + apiData.tiktok.avgShares || 0
            }
        };
    }
    
    return result;
}

/**
 * Create followers comparison chart
 * @param {Object} data - Social media data
 */
function createFollowersChart(data) {
    const ctx = document.getElementById('followersChart').getContext('2d');
    
    const platforms = [];
    const followers = [];
    const colors = [];
    
    if (data.facebook) {
        platforms.push('Facebook');
        followers.push(data.facebook.followers);
        colors.push('#1877f2');
    }
    
    if (data.instagram) {
        platforms.push('Instagram');
        followers.push(data.instagram.followers);
        colors.push('#e4405f');
    }
    
    if (data.youtube) {
        platforms.push('YouTube');
        followers.push(data.youtube.followers);
        colors.push('#ff0000');
    }
    
    if (data.linkedin) {
        platforms.push('LinkedIn');
        followers.push(data.linkedin.followers);
        colors.push('#0077b5');
    }
    
    if (data.twitter) {
        platforms.push('Twitter/X');
        followers.push(data.twitter.followers);
        colors.push('#1da1f2');
    }
    
    if (data.tiktok) {
        platforms.push('TikTok');
        followers.push(data.tiktok.followers);
        colors.push('#000000');
    }
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: platforms,
            datasets: [{
                label: 'Followers',
                data: followers,
                backgroundColor: colors,
                borderColor: colors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            if (value >= 1000000) {
                                return (value / 1000000).toFixed(1) + 'M';
                            } else if (value >= 1000) {
                                return (value / 1000).toFixed(1) + 'K';
                            }
                            return value;
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let value = context.raw;
                            if (value >= 1000000) {
                                return (value / 1000000).toFixed(1) + 'M followers';
                            } else if (value >= 1000) {
                                return (value / 1000).toFixed(1) + 'K followers';
                            }
                            return value + ' followers';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Create engagement rate chart
 * @param {Object} data - Social media data
 */
function createEngagementChart(data) {
    const ctx = document.getElementById('engagementChart').getContext('2d');
    
    const platforms = [];
    const engagementRates = [];
    const colors = [];
    
    if (data.facebook) {
        platforms.push('Facebook');
        const rate = (data.facebook.engagement.total_engagement / data.facebook.followers) * 100;
        engagementRates.push(parseFloat(rate.toFixed(2)) || 0);
        colors.push('#1877f2');
    }
    
    if (data.instagram) {
        platforms.push('Instagram');
        const rate = (data.instagram.engagement.total_engagement / data.instagram.followers) * 100;
        engagementRates.push(parseFloat(rate.toFixed(2)) || 0);
        colors.push('#e4405f');
    }
    
    if (data.youtube) {
        platforms.push('YouTube');
        const rate = (data.youtube.engagement.total_engagement / data.youtube.followers) * 100;
        engagementRates.push(parseFloat(rate.toFixed(2)) || 0);
        colors.push('#ff0000');
    }
    
    if (data.linkedin) {
        platforms.push('LinkedIn');
        const rate = (data.linkedin.engagement.total_engagement / data.linkedin.followers) * 100;
        engagementRates.push(parseFloat(rate.toFixed(2)) || 0);
        colors.push('#0077b5');
    }
    
    if (data.twitter) {
        platforms.push('Twitter/X');
        const rate = (data.twitter.engagement.total_engagement / data.twitter.followers) * 100;
        engagementRates.push(parseFloat(rate.toFixed(2)) || 0);
        colors.push('#1da1f2');
    }
    
    if (data.tiktok) {
        platforms.push('TikTok');
        const rate = (data.tiktok.engagement.total_engagement / data.tiktok.followers) * 100;
        engagementRates.push(parseFloat(rate.toFixed(2)) || 0);
        colors.push('#000000');
    }
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: platforms,
            datasets: [{
                label: 'Engagement Rate (%)',
                data: engagementRates,
                backgroundColor: colors,
                borderColor: colors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.raw + '% engagement rate';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Create post frequency chart
 * @param {Object} data - Social media data
 */
function createPostFrequencyChart(data) {
    const ctx = document.getElementById('postFrequencyChart').getContext('2d');
    
    const platforms = [];
    const postCounts = [];
    const colors = [];
    
    if (data.facebook) {
        platforms.push('Facebook');
        postCounts.push(data.facebook.engagement.posts);
        colors.push('#1877f2');
    }
    
    if (data.instagram) {
        platforms.push('Instagram');
        postCounts.push(data.instagram.engagement.posts);
        colors.push('#e4405f');
    }
    
    if (data.youtube) {
        platforms.push('YouTube');
        postCounts.push(data.youtube.engagement.posts);
        colors.push('#ff0000');
    }
    
    if (data.linkedin) {
        platforms.push('LinkedIn');
        postCounts.push(data.linkedin.engagement.posts);
        colors.push('#0077b5');
    }
    
    if (data.twitter) {
        platforms.push('Twitter/X');
        postCounts.push(data.twitter.engagement.posts);
        colors.push('#1da1f2');
    }
    
    if (data.tiktok) {
        platforms.push('TikTok');
        postCounts.push(data.tiktok.engagement.posts);
        colors.push('#000000');
    }
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: platforms,
            datasets: [{
                label: 'Posts',
                data: postCounts,
                backgroundColor: colors,
                borderColor: colors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

/**
 * Populate performance table
 * @param {Object} data - Social media data
 */
function populatePerformanceTable(data) {
    const tableBody = document.getElementById('performanceTableBody');
    tableBody.innerHTML = '';
    
    const platforms = [
        { key: 'facebook', name: 'Facebook', icon: 'facebook' },
        { key: 'instagram', name: 'Instagram', icon: 'instagram' },
        { key: 'youtube', name: 'YouTube', icon: 'youtube' },
        { key: 'linkedin', name: 'LinkedIn', icon: 'linkedin' },
        { key: 'twitter', name: 'Twitter/X', icon: 'twitter' },
        { key: 'tiktok', name: 'TikTok', icon: 'tiktok' }
    ];
    
    platforms.forEach(platform => {
        if (data[platform.key]) {
            const platformData = data[platform.key];
            const engagement = platformData.engagement;
            
            // Calculate engagement rate
            const engagementRate = ((engagement.total_engagement || 0) / (platformData.followers || 1) * 100).toFixed(2);
            
            // Calculate performance score (simple algorithm for demo)
            const followersScore = Math.log10(Math.max(1, platformData.followers)) * 10;
            const engagementScore = parseFloat(engagementRate) * 5;
            const postScore = Math.log10(Math.max(1, engagement.posts)) * 5;
            const performanceScore = Math.min(100, Math.round(followersScore + engagementScore + postScore));
            
            // Create table row
            const row = document.createElement('tr');
            
            // Platform column
            const platformCell = document.createElement('td');
            platformCell.innerHTML = `<i class="bi bi-${platform.icon} platform-icon ${platform.key}-color"></i> ${platform.name}`;
            row.appendChild(platformCell);
            
            // Followers column
            const followersCell = document.createElement('td');
            followersCell.textContent = formatNumber(platformData.followers);
            row.appendChild(followersCell);
            
            // Posts column
            const postsCell = document.createElement('td');
            postsCell.textContent = engagement.posts;
            row.appendChild(postsCell);
            
            // Avg. Engagement column
            const avgEngagementCell = document.createElement('td');
            avgEngagementCell.textContent = engagement.total_engagement || 'N/A';
            row.appendChild(avgEngagementCell);
            
            // Engagement Rate column
            const engagementRateCell = document.createElement('td');
            engagementRateCell.textContent = engagementRate + '%';
            row.appendChild(engagementRateCell);
            
            // Performance Score column
            const performanceScoreCell = document.createElement('td');
            performanceScoreCell.innerHTML = `
                <div class="progress" style="height: 20px;">
                    <div class="progress-bar bg-${getPerformanceColor(performanceScore)}" 
                         role="progressbar" 
                         style="width: ${performanceScore}%;" 
                         aria-valuenow="${performanceScore}" 
                         aria-valuemin="0" 
                         aria-valuemax="100">
                        ${performanceScore}/100
                    </div>
                </div>
            `;
            row.appendChild(performanceScoreCell);
            
            tableBody.appendChild(row);
        }
    });
}

/**
 * Generate recommendations based on data
 * @param {Object} data - Social media data
 */
function generateRecommendations(data) {
    const recommendationsContainer = document.getElementById('recommendationsContainer');
    recommendationsContainer.innerHTML = '';
    
    const recommendations = [];
    
    // Find platform with highest engagement rate
    let highestEngagementRate = 0;
    let highestEngagementPlatform = '';
    
    // Find platform with lowest engagement rate
    let lowestEngagementRate = Infinity;
    let lowestEngagementPlatform = '';
    
    // Calculate engagement rates for each platform
    Object.entries(data).forEach(([key, value]) => {
        if (key !== 'website' && value && value.followers && value.engagement && value.engagement.total_engagement) {
            const engagementRate = (value.engagement.total_engagement / value.followers) * 100;
            
            if (engagementRate > highestEngagementRate) {
                highestEngagementRate = engagementRate;
                highestEngagementPlatform = key;
            }
            
            if (engagementRate < lowestEngagementRate && engagementRate > 0) {
                lowestEngagementRate = engagementRate;
                lowestEngagementPlatform = key;
            }
        }
    });
    
    // Add recommendations based on findings
    if (highestEngagementPlatform) {
        const platformName = highestEngagementPlatform.charAt(0).toUpperCase() + highestEngagementPlatform.slice(1);
        recommendations.push({
            title: `Leverage ${platformName} Success`,
            description: `Your ${platformName} account has the highest engagement rate (${highestEngagementRate.toFixed(2)}%). Consider analyzing what content performs well there and adapt similar strategies for other platforms.`,
            icon: 'trophy'
        });
    }
    
    if (lowestEngagementPlatform && lowestEngagementRate < Infinity) {
        const platformName = lowestEngagementPlatform.charAt(0).toUpperCase() + lowestEngagementPlatform.slice(1);
        recommendations.push({
            title: `Improve ${platformName} Engagement`,
            description: `Your ${platformName} account has the lowest engagement rate (${lowestEngagementRate.toFixed(2)}%). Consider revising your content strategy or posting frequency to better engage your audience.`,
            icon: 'arrow-up-circle'
        });
    }
    
    // Add general recommendations
    recommendations.push({
        title: 'Cross-Platform Content Strategy',
        description: 'Develop a cohesive content strategy across all platforms while adapting to each platform\'s unique features and audience preferences.',
        icon: 'grid'
    });
    
    recommendations.push({
        title: 'Engagement Analysis',
        description: 'Analyze which types of content generate the most engagement and focus your efforts on creating more of that content.',
        icon: 'graph-up'
    });
    
    recommendations.push({
        title: 'Posting Schedule Optimization',
        description: 'Test different posting times and frequencies to determine when your audience is most active and responsive.',
        icon: 'calendar-check'
    });
    
    // Display recommendations
    recommendations.forEach(recommendation => {
        const card = document.createElement('div');
        card.className = 'card mb-3';
        card.innerHTML = `
            <div class="card-body">
                <h5 class="card-title">
                    <i class="bi bi-${recommendation.icon} me-2"></i>
                    ${recommendation.title}
                </h5>
                <p class="card-text">${recommendation.description}</p>
            </div>
        `;
        recommendationsContainer.appendChild(card);
    });
}

/**
 * Get color based on performance score
 * @param {number} score - Performance score
 * @returns {string} - Bootstrap color class
 */
function getPerformanceColor(score) {
    if (score >= 80) return 'success';
    if (score >= 60) return 'info';
    if (score >= 40) return 'warning';
    return 'danger';
}

/**
 * Format number with K/M suffix for readability
 * @param {number} num - Number to format
 * @returns {string} - Formatted number
 */
function formatNumber(num) {
    if (!num) return '0';
    
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}
