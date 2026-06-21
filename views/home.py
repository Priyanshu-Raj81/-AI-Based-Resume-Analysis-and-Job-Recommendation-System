import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def render_home():
    # --- Custom CSS for Animations & Hover Effects ---
    st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Animated Hero Banner */
        .hero-banner {
            border-radius: 16px; padding: 48px 40px;
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            text-align: center; margin-bottom: 36px; color: white;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            transition: transform 0.3s ease;
        }
        .hero-banner:hover { transform: translateY(-5px); }
        
        /* Bouncing Icon Animation */
        .hero-icon { 
            font-size: 50px; 
            margin-bottom: 12px; 
            animation: bounce 2s infinite; 
        }
        @keyframes bounce { 
            0%, 100% { transform: translateY(0); } 
            50% { transform: translateY(-12px); } 
        }
        
        .hero-title { font-size: 36px; font-weight: 800; margin-bottom: 8px; letter-spacing: 1px;}
        .hero-sub { font-size: 16px; color: rgba(255,255,255,0.85); }
        
        /* Interactive Stat Cards */
        .stat-card { 
            background: #1a2035; border: 1px solid #2a3352; 
            border-radius: 12px; padding: 18px 20px; color: #e8eaf0; 
            transition: all 0.3s ease; cursor: default;
        }
        .stat-card:hover { 
            border-color: #3b82f6; 
            box-shadow: 0 0 20px rgba(59,130,246,0.2); 
            transform: translateY(-8px); 
        }
        .stat-label { font-size: 14px; color: #8b93ac; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }
        .stat-val { font-size: 28px; font-weight: 800; margin-bottom: 10px; color: #ffffff;}
        .stat-badge { background: rgba(34,197,94,0.15); color: #4ade80; font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

    # --- Hero Banner ---
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-icon">🎯</div>
        <div class="hero-title">Resumatch AI</div>
        <div class="hero-sub">Your Smart Career & Resume Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)

    # --- Dashboard Overview (Stats) ---
    st.markdown("### 📊 System Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown('<div class="stat-card"><div class="stat-label">📋 Skills Tracked</div><div class="stat-val">50+</div><span class="stat-badge">↑ Dynamic</span></div>', unsafe_allow_html=True)
    with col2: st.markdown('<div class="stat-card"><div class="stat-label">🎯 Career Paths</div><div class="stat-val">25+</div><span class="stat-badge">↑ Updated</span></div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="stat-card"><div class="stat-label">🧠 AI Engine</div><div class="stat-val">Groq</div><span class="stat-badge">⚡ Active</span></div>', unsafe_allow_html=True)
    with col4: st.markdown('<div class="stat-card"><div class="stat-label">⚡ Parsing Speed</div><div class="stat-val">&lt; 2s</div><span class="stat-badge">🚀 Fast</span></div>', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # --- Interactive Charts Section ---
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("### 🔥 Trending Tech Skills")
        
        # Data for Skills
        skills_df = pd.DataFrame({
            "Skill": ['Generative AI', 'Cloud (AWS/GCP)', 'Python', 'Machine Learning', 'Flutter/Dart'],
            "Demand": [98, 92, 88, 85, 80]
        })
        
        # Interactive Horizontal Bar Chart
        fig_skills = go.Figure(go.Bar(
            x=skills_df['Demand'],
            y=skills_df['Skill'],
            orientation='h',
            marker=dict(
                color=skills_df['Demand'],
                colorscale='Blues',
                line=dict(color='rgba(0,0,0,0)', width=1)
            ),
            text=[f"{val}%" for val in skills_df['Demand']],
            textposition='inside',
            hoverinfo='y+text'
        ))
        
        fig_skills.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8b93ac'),
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(autorange="reversed", showgrid=False, tickfont=dict(size=14, color='white')),
            margin=dict(l=0, r=0, t=10, b=0),
            height=320,
            hovermode="y unified"
        )
        st.plotly_chart(fig_skills, use_container_width=True)

    with col_chart2:
        st.markdown("### 💼 Fastest Growing Roles")
        
        # Data for Jobs
        jobs_df = pd.DataFrame({
            "Role": ['AI Engineer', 'Data Scientist', 'Cloud Architect', 'Full Stack Dev', 'Security Analyst'],
            "Growth": [40, 25, 15, 12, 8]
        })
        
        # Interactive Donut Chart
        fig_jobs = go.Figure(data=[go.Pie(
            labels=jobs_df['Role'],
            values=jobs_df['Growth'],
            hole=.6,
            marker=dict(colors=['#7c3aed', '#3b82f6', '#06b6d4', '#10b981', '#f59e0b']),
            hoverinfo="label+percent",
            textinfo="percent",
            textfont_size=14,
            pull=[0.1, 0, 0, 0, 0] # Pulls the first slice (AI Engineer) out slightly for a cool effect
        )])
        
        fig_jobs.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8b93ac'),
            showlegend=True,
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1),
            margin=dict(l=0, r=0, t=10, b=0),
            height=320,
            annotations=[dict(text='Roles', x=0.5, y=0.5, font_size=20, font_color="white", showarrow=False)]
        )
        st.plotly_chart(fig_jobs, use_container_width=True)