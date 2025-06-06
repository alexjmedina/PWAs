/**
 * KPIs Social Extractor - Dashboard JavaScript
 * Handles chart creation and data visualization for the dashboard page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Sample data (in a real application, this would come from the backend)
    const sampleData = {
        facebook: {
            followers: 65200,
            engagement: {
                posts: 120,
                avg_likes: 450,
                avg_comments: 35,
                total_engagement: 485
            }
        },
        instagram: {
            followers: 24500,
            engagement: {
                posts: 85,
                avg_likes: 780,
                avg_comments: 42,
                total_engagement: 822
            }
        },
        youtube: {
            followers: 3510,
            engagement: {
                posts: 45,
                avg_likes: 120,
                avg_comments: 18,
                avg_views: 1500,
                total_engagement: 138
            }
        },
        linkedin: {
            followers: 28000,
            engagement: {
                posts: 65,
                avg_likes: 95,
                avg_comments: 12,
                total_engagement: 107
            }
        },
        twitter: {
            followers: 5700,
            engagement: {
                posts: 210,
                avg_likes: 25,
                avg_retweets: 8,
                avg_replies: 3,
                total_engagement: 36
            }
        },
        tiktok: {
            followers: 18700,
            engagement: {
                posts: 60,
                avg_likes: 2300,
                avg_comments: 85,
                total_engagement: 2385
            }
        }
    };
    
    // Create charts
    createFollowersChart(sampleData);
    createEngagementChart(sampleData);
    createPostFrequencyChart(sampleData);
    
    // Populate performance table
    populatePerformanceTable(sampleData);
    
    // Generate recommendations
    generateRecommendations(sampleData);
});

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
        engagementRates.push(parseFloat(rate.toFixed(2)));
        colors.push('#1877f2');
    }
    
    if (data.instagram) {
        platforms.push('Instagram');
        const rate = (data.instagram.engagement.total_engagement / data.instagram.followers) * 100;
        engagementRates.push(parseFloat(rate.toFixed(2)));
        colors.push('#e4405f');
    }
    
    if (data.youtube) {
        platforms.push('YouTube');
        const rate = (data.youtube.engagement.total_engagement / data.youtube.followers) * 100;
        engagementRates.push(parseFloat(rate.toFixed(2)));
        colors.push('#ff0000');
    }
    
    if (data.linkedin) {
        platforms.push('LinkedIn');
        const rate = (data.linkedin.engagement.total_engagement / data.linkedin.followers) * 100;
        engagementRates.push(parseFloat(rate.toFixed(2)));
        colors.push('#0077b5');
    }
    
    if (data.twitter) {
        platforms.push('Twitter/X');
        const rate = (data.twitter.engagement.total_engagement / data.twitter.followers) * 100;
        engagementRates.push(parseFloat(rate.toFixed(2)));
        colors.push('#1da1f2');
    }
    
    if (data.tiktok) {
        platforms.push('TikTok');
        const rate = (data.tiktok.engagement.total_engagement / data.tiktok.followers) * 100;
        engagementRates.push(parseFloat(rate.toFixed(2)));
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
            const engagementRate = ((engagement.total_engagement || 0) / platformData.followers * 100).toFixed(2);
            
            // Calculate performance score (simple algorithm for demo)
            const followersScore = Math.log10(platformData.followers) * 10;
            const engagementScore = parseFloat(engagementRate) * 5;
            const postScore = Math.log10(engagement.posts) * 5;
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
            
            if (engagementRate < lowestEngagementRate) {
                lowestEngagementRate = engagementRate;
                lowestEngagementPlatform = engagementRate > 0 ? key : lowestEngagementPlatform;
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
        title: 'Regular Analytics Review',
        description: 'Schedule monthly reviews of your social media analytics to track progress and adjust strategies based on performance data.',
        icon: 'graph-up'
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
 * Get color class based on performance score
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
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}
