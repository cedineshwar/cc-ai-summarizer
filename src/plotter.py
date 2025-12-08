"""
Plotting module for generating various charts and graphs from call center summaries.
Supports bar charts, pie charts, line charts, scatter plots, and more.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np
import json
import io
import base64
from typing import Tuple, Optional, Dict, Any
from src.logger import logger

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


def encode_plot_to_base64(fig) -> str:
    """Convert matplotlib figure to base64 string for embedding in Streamlit."""
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode()
    plt.close(fig)
    return img_base64


def extract_numeric_value(value: Any) -> float:
    """Safely extract numeric value from various types."""
    try:
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str):
            # Try to convert string to float
            return float(value)
        else:
            return 0.0
    except (ValueError, TypeError):
        return 0.0


def generate_agent_performance_bar_chart(summaries: list) -> Tuple[str, str]:
    """Generate bar chart showing agent performance scores."""
    try:
        if not summaries:
            return None, "No data available"
        
        # Extract agent data
        agents_data = {}
        for summary in summaries:
            agent_name = summary.get('agentName', 'Unknown')
            agent_score = extract_numeric_value(summary.get('agentScore', 0))
            
            if agent_name not in agents_data:
                agents_data[agent_name] = []
            agents_data[agent_name].append(agent_score)
        
        # Calculate average scores
        avg_scores = {name: np.mean(scores) for name, scores in agents_data.items()}
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        names = list(avg_scores.keys())
        scores = list(avg_scores.values())
        
        colors = ['#2ecc71' if score >= 80 else '#f39c12' if score >= 60 else '#e74c3c' 
                  for score in scores]
        bars = ax.bar(names, scores, color=colors, edgecolor='black', linewidth=1.2)
        
        # Add value labels on bars
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{score:.1f}',
                   ha='center', va='bottom', fontweight='bold')
        
        ax.set_ylabel('Average Agent Score', fontsize=12, fontweight='bold')
        ax.set_xlabel('Agent Name', fontsize=12, fontweight='bold')
        ax.set_title('Agent Performance Scores', fontsize=14, fontweight='bold', pad=20)
        ax.set_ylim(0, 100)
        ax.axhline(y=80, color='green', linestyle='--', alpha=0.5, label='Excellent (80+)')
        ax.axhline(y=60, color='orange', linestyle='--', alpha=0.5, label='Good (60+)')
        ax.legend()
        plt.xticks(rotation=45, ha='right')
        
        img_base64 = encode_plot_to_base64(fig)
        summary_text = f"Generated agent performance bar chart with {len(agents_data)} agents. Average scores range from {min(scores):.1f} to {max(scores):.1f}."
        
        return img_base64, summary_text
    except Exception as e:
        logger.error(f"Error generating agent performance bar chart: {e}")
        return None, f"Error generating chart: {str(e)}"


def generate_agent_score_distribution_pie(summaries: list) -> Tuple[str, str]:
    """Generate pie chart showing distribution of agent scores by performance level."""
    try:
        if not summaries:
            return None, "No data available"
        
        # Categorize scores
        excellent = sum(1 for s in summaries if extract_numeric_value(s.get('agentScore', 0)) >= 85)
        very_good = sum(1 for s in summaries if 75 <= extract_numeric_value(s.get('agentScore', 0)) < 85)
        good = sum(1 for s in summaries if 60 <= extract_numeric_value(s.get('agentScore', 0)) < 75)
        needs_improvement = sum(1 for s in summaries if extract_numeric_value(s.get('agentScore', 0)) < 60)
        
        # Create pie chart
        fig, ax = plt.subplots(figsize=(10, 8))
        sizes = [excellent, very_good, good, needs_improvement]
        labels = [f'Excellent (85+)\n{excellent}', f'Very Good (75-84)\n{very_good}', 
                 f'Good (60-74)\n{good}', f'Needs Improvement (<60)\n{needs_improvement}']
        colors = ['#27ae60', '#2ecc71', '#f39c12', '#e74c3c']
        explode = (0.05, 0.05, 0, 0)
        
        wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                           autopct='%1.1f%%', shadow=True, startangle=90,
                                           textprops={'fontsize': 11, 'fontweight': 'bold'})
        
        ax.set_title('Agent Performance Distribution', fontsize=14, fontweight='bold', pad=20)
        
        img_base64 = encode_plot_to_base64(fig)
        summary_text = f"Score distribution: Excellent ({excellent}), Very Good ({very_good}), Good ({good}), Needs Improvement ({needs_improvement})"
        
        return img_base64, summary_text
    except Exception as e:
        logger.error(f"Error generating score distribution pie chart: {e}")
        return None, f"Error generating chart: {str(e)}"


def generate_conversation_duration_chart(summaries: list) -> Tuple[str, str]:
    """Generate bar chart showing conversation durations."""
    try:
        if not summaries:
            return None, "No data available"
        
        # Extract duration data
        durations = []
        agents = []
        for summary in summaries:
            duration_str = summary.get('conversationlength', '0')
            # Parse duration (e.g., "9 mins", "26 minutes")
            duration_str = duration_str.lower().replace('mins', '').replace('minutes', '').replace('min', '').strip()
            try:
                duration = float(duration_str)
                durations.append(duration)
                agents.append(summary.get('agentName', 'Unknown')[:15])  # Truncate long names
            except ValueError:
                pass
        
        if not durations:
            return None, "Could not parse conversation durations"
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        x_pos = np.arange(len(agents))
        colors = plt.cm.viridis(np.linspace(0, 1, len(durations)))
        
        bars = ax.bar(x_pos, durations, color=colors, edgecolor='black', linewidth=1.2)
        
        # Add value labels
        for bar, duration in zip(bars, durations):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{duration:.0f}m',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax.set_xlabel('Agent', fontsize=12, fontweight='bold')
        ax.set_ylabel('Duration (minutes)', fontsize=12, fontweight='bold')
        ax.set_title('Call Duration by Agent', fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(agents, rotation=45, ha='right')
        ax.grid(axis='y', alpha=0.3)
        
        img_base64 = encode_plot_to_base64(fig)
        avg_duration = np.mean(durations)
        summary_text = f"Average call duration: {avg_duration:.1f} minutes. Range: {min(durations):.0f} - {max(durations):.0f} minutes"
        
        return img_base64, summary_text
    except Exception as e:
        logger.error(f"Error generating conversation duration chart: {e}")
        return None, f"Error generating chart: {str(e)}"


def generate_agent_vs_conversation_count(summaries: list) -> Tuple[str, str]:
    """Generate bar chart showing number of conversations per agent."""
    try:
        if not summaries:
            return None, "No data available"
        
        # Count conversations per agent
        agent_counts = {}
        for summary in summaries:
            agent_name = summary.get('agentName', 'Unknown')
            agent_counts[agent_name] = agent_counts.get(agent_name, 0) + 1
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        names = sorted(agent_counts.keys())
        counts = [agent_counts[name] for name in names]
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(names)))
        bars = ax.bar(names, counts, color=colors, edgecolor='black', linewidth=1.2)
        
        # Add value labels
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{count}',
                   ha='center', va='bottom', fontweight='bold')
        
        ax.set_xlabel('Agent Name', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Conversations', fontsize=12, fontweight='bold')
        ax.set_title('Conversation Count by Agent', fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        
        img_base64 = encode_plot_to_base64(fig)
        summary_text = f"Total conversations: {sum(counts)} across {len(names)} agents. Agent with most calls: {max(agent_counts, key=agent_counts.get)} ({max(counts)} calls)"
        
        return img_base64, summary_text
    except Exception as e:
        logger.error(f"Error generating agent vs conversation count chart: {e}")
        return None, f"Error generating chart: {str(e)}"


def generate_customer_sentiment_distribution(summaries: list) -> Tuple[str, str]:
    """Generate pie chart showing customer sentiment distribution."""
    try:
        if not summaries:
            return None, "No data available"
        
        # Extract sentiment data
        sentiments = {}
        for summary in summaries:
            tone = summary.get('customerTone', 'Unknown').lower()
            sentiments[tone] = sentiments.get(tone, 0) + 1
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 8))
        labels = list(sentiments.keys())
        sizes = list(sentiments.values())
        
        # Color mapping for different sentiments
        color_map = {
            'happy': '#2ecc71',
            'satisfied': '#27ae60',
            'neutral': '#95a5a6',
            'upset': '#e67e22',
            'angry': '#e74c3c',
            'frustrated': '#f39c12',
            'calm': '#3498db',
            'professional': '#34495e',
            'appreciative': '#9b59b6',
            'worried': '#e74c3c',
            'alarm': '#c0392b'
        }
        
        colors = [color_map.get(label, '#95a5a6') for label in labels]
        explode = [0.05 if size == max(sizes) else 0 for size in sizes]
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                           shadow=True, startangle=90, explode=explode,
                                           textprops={'fontsize': 10, 'fontweight': 'bold'})
        
        ax.set_title('Customer Sentiment Distribution', fontsize=14, fontweight='bold', pad=20)
        
        img_base64 = encode_plot_to_base64(fig)
        summary_text = f"Customer sentiment breakdown: {', '.join([f'{tone.capitalize()} ({count})' for tone, count in sentiments.items()])}"
        
        return img_base64, summary_text
    except Exception as e:
        logger.error(f"Error generating customer sentiment distribution: {e}")
        return None, f"Error generating chart: {str(e)}"


def generate_agent_rating_distribution(summaries: list) -> Tuple[str, str]:
    """Generate bar chart showing distribution of agent ratings (1-5 stars)."""
    try:
        if not summaries:
            return None, "No data available"
        
        # Count ratings
        rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for summary in summaries:
            rating = int(extract_numeric_value(summary.get('agentRating', 3)))
            if 1 <= rating <= 5:
                rating_counts[rating] += 1
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        ratings = list(rating_counts.keys())
        counts = list(rating_counts.values())
        
        colors = ['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71', '#27ae60']
        bars = ax.bar(ratings, counts, color=colors, edgecolor='black', linewidth=1.2, width=0.6)
        
        # Add value labels
        for bar, count in zip(bars, counts):
            if count > 0:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{count}',
                       ha='center', va='bottom', fontweight='bold')
        
        ax.set_xlabel('Rating (Stars)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Calls', fontsize=12, fontweight='bold')
        ax.set_title('Agent Rating Distribution', fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(ratings)
        # Use numeric labels with star descriptions instead of emoji
        ax.set_xticklabels(['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars'])
        ax.grid(axis='y', alpha=0.3)
        
        img_base64 = encode_plot_to_base64(fig)
        avg_rating = sum(r * c for r, c in zip(ratings, counts)) / sum(counts) if sum(counts) > 0 else 0
        summary_text = f"Average agent rating: {avg_rating:.2f}/5 stars. Distribution: {', '.join([f'{r} star(s) ({count} calls)' for r, count in rating_counts.items() if count > 0])}"
        
        return img_base64, summary_text
    except Exception as e:
        logger.error(f"Error generating agent rating distribution: {e}")
        return None, f"Error generating chart: {str(e)}"


def generate_resolution_status_chart(summaries: list) -> Tuple[str, str]:
    """Generate pie chart showing resolution status of calls."""
    try:
        if not summaries:
            return None, "No data available"
        
        # Extract resolution data from resolutionStatus field
        resolved = sum(1 for s in summaries if 'Resolved' in s.get('resolutionStatus', '') 
                      and 'Unresolved' not in s.get('resolutionStatus', ''))
        unresolved = len(summaries) - resolved
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 8))
        sizes = [resolved, unresolved]
        labels = [f'Resolved\n{resolved}', f'Unresolved\n{unresolved}']
        colors = ['#2ecc71', '#e74c3c']
        explode = (0.05, 0.05)
        
        wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                           autopct='%1.1f%%', shadow=True, startangle=90,
                                           textprops={'fontsize': 12, 'fontweight': 'bold'})
        
        ax.set_title('Call Resolution Status', fontsize=14, fontweight='bold', pad=20)
        
        img_base64 = encode_plot_to_base64(fig)
        resolution_rate = (resolved / len(summaries) * 100) if summaries else 0
        summary_text = f"Overall resolution rate: {resolution_rate:.1f}% ({resolved}/{len(summaries)} calls resolved)"
        
        return img_base64, summary_text
    except Exception as e:
        logger.error(f"Error generating resolution status chart: {e}")
        return None, f"Error generating chart: {str(e)}"


def detect_chart_request(user_message: str) -> Optional[str]:
    """Detect if user is requesting a chart/graph and return the type."""
    message_lower = user_message.lower()
    
    chart_keywords = {
        'agent performance': ['agent performance', 'agent scores', 'performance scores', 'agent skill'],
        'score distribution': ['score distribution', 'performance distribution', 'score breakdown'],
        'duration': ['call duration', 'conversation length', 'duration', 'time spent'],
        'agent count': ['agent count', 'conversation count', 'calls per agent', 'agent vs conversation'],
        'sentiment': ['sentiment', 'customer tone', 'emotion', 'customer mood'],
        'rating': ['rating', 'ratings', 'stars', 'agent rating'],
        'resolution': ['resolution', 'resolved', 'unresolved', 'resolution status'],
    }
    
    for chart_type, keywords in chart_keywords.items():
        if any(keyword in message_lower for keyword in keywords):
            return chart_type
    
    # Generic chart requests
    if any(keyword in message_lower for keyword in ['chart', 'graph', 'plot', 'visualization', 'diagram']):
        return 'agent performance'  # Default to agent performance
    
    return None


def generate_chart(chart_type: str, summaries: list) -> Tuple[Optional[str], str]:
    """Generate appropriate chart based on type requested."""
    chart_generators = {
        'agent performance': generate_agent_performance_bar_chart,
        'score distribution': generate_agent_score_distribution_pie,
        'duration': generate_conversation_duration_chart,
        'agent count': generate_agent_vs_conversation_count,
        'sentiment': generate_customer_sentiment_distribution,
        'rating': generate_agent_rating_distribution,
        'resolution': generate_resolution_status_chart,
    }
    
    generator = chart_generators.get(chart_type, generate_agent_performance_bar_chart)
    return generator(summaries)
