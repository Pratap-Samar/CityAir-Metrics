import React from 'react';
import './About.css';
import { Target, Users, BarChart3, Cloud, Wind, Database, Settings, Clock, Calendar, CheckCircle2, AlertTriangle, Info,  ExternalLink, Leaf } from 'lucide-react';
import type { DashboardSummary } from '../types';

interface AboutProps {
  summary: DashboardSummary | null;
}

export const About: React.FC<AboutProps> = ({ summary }) => {
  const totalCities = summary?.total_cities || 36;

  return (
    <div className="about-page-wrapper">
      <div className="about-header-section">
        <div className="about-title-area">
          <h1>About CityAir Metrics</h1>
          <p>Data-driven insights for cleaner, healthier cities</p>
        </div>
        <div className="about-quote-box">
          <Leaf className="quote-icon" size={24} />
          <span>"Cleaner air today for a healthier tomorrow."</span>
        </div>
      </div>

      <div className="about-mission-grid">
        <div className="about-card">
          <div className="card-icon-wrapper blue">
            <Target size={28} />
          </div>
          <h3>Our Mission</h3>
          <p>To make environmental data accessible, actionable and easy to understand, helping people, cities and policymakers build cleaner and healthier urban environments.</p>
        </div>
        <div className="about-card">
          <div className="card-icon-wrapper green">
            <Users size={28} />
          </div>
          <h3>What We Do</h3>
          <p>CityAir Metrics collects, processes and visualizes air quality and weather data for all Indian state capitals, providing real-time insights, comparisons and trends in a simple, intuitive interface.</p>
        </div>
        <div className="about-card">
          <div className="card-icon-wrapper purple">
            <BarChart3 size={28} />
          </div>
          <h3>Who It's For</h3>
          <p>Citizens, researchers, students and policymakers who want to understand air quality trends and make data-driven decisions for healthier, more sustainable cities.</p>
        </div>
      </div>

      <div className="about-middle-grid">
        <div className="about-card">
          <h2 className="section-title">Data Sources</h2>
          <p className="section-subtitle">We use reliable, open data sources to ensure transparency and accuracy.</p>
          
          <div className="source-item">
            <div className="source-icon-wrapper blue">
              <Cloud size={24} />
            </div>
            <div className="source-content">
              <div className="source-header">
                <h4>Weather Data</h4>
                <a href="https://open-meteo.com" target="_blank" rel="noreferrer" className="source-link">
                  <ExternalLink size={14} /> open-meteo.com
                </a>
              </div>
              <div className="source-desc">Open-Meteo</div>
              <p>Temperature, humidity, wind, precipitation and other meteorological data.</p>
            </div>
          </div>

          <div className="source-item">
            <div className="source-icon-wrapper purple">
              <Wind size={24} />
            </div>
            <div className="source-content">
              <div className="source-header">
                <h4>Air Quality Data</h4>
                <a href="https://open-meteo.com" target="_blank" rel="noreferrer" className="source-link">
                  <ExternalLink size={14} /> open-meteo.com
                </a>
              </div>
              <div className="source-desc">Open-Meteo (Air Quality API)</div>
              <p>AQI, PM2.5, PM10 and other pollutants for major Indian cities.</p>
            </div>
          </div>
        </div>

        <div className="about-card">
          <h2 className="section-title">How It Works</h2>
          <p className="section-subtitle">From raw data to actionable insights.</p>
          
          <div className="how-it-works-flow">
            <div className="flow-step">
              <div className="flow-icon blue">
                <Database size={24} />
              </div>
              <h4>1. Data Collection</h4>
              <p>Fetch weather and air quality data from open sources</p>
            </div>
            <div className="flow-arrow">→</div>
            <div className="flow-step">
              <div className="flow-icon green">
                <Settings size={24} />
              </div>
              <h4>2. Data Processing</h4>
              <p>Clean, validate and enrich the data</p>
            </div>
            <div className="flow-arrow">→</div>
            <div className="flow-step">
              <div className="flow-icon purple">
                <Database size={24} />
              </div>
              <h4>3. Storage</h4>
              <p>Store processed data in a database</p>
            </div>
            <div className="flow-arrow">→</div>
            <div className="flow-step">
              <div className="flow-icon orange">
                <BarChart3 size={24} />
              </div>
              <h4>4. Visualization</h4>
              <p>Present insights through interactive dashboards and maps</p>
            </div>
          </div>
        </div>
      </div>

      <div className="about-bottom-grid">
        <div className="about-card">
          <h2 className="section-title">Technology Stack</h2>
          <p className="section-subtitle">Built with modern, open-source technologies.</p>
          
          <div className="tech-stack-flex">
            <div className="tech-item">
              <img src="https://upload.wikimedia.org/wikipedia/commons/a/a7/React-icon.svg" alt="React" className="tech-logo" />
              <strong>React</strong>
              <span>Frontend</span>
            </div>
            <div className="tech-item">
              <img src="https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.svg" alt="Python" className="tech-logo" />
              <strong>Python</strong>
              <span>Data Processing</span>
            </div>
            <div className="tech-item">
              <img src="https://upload.wikimedia.org/wikipedia/commons/2/29/Postgresql_elephant.svg" alt="PostgreSQL" className="tech-logo" />
              <strong>PostgreSQL</strong>
              <span>Database</span>
            </div>
            <div className="tech-item">
              <img src="https://upload.wikimedia.org/wikipedia/commons/4/4e/Docker_%28container_engine%29_logo.svg" alt="Docker" className="tech-logo" />
              <strong>Docker</strong>
              <span>Deployment</span>
            </div>
            <div className="tech-item">
              <Cloud className="tech-logo" style={{ color: "#3b82f6" }} size={42} />
              <strong>Open-Meteo</strong>
              <span>Data Source</span>
            </div>
          </div>
        </div>

        <div className="about-card">
          <h2 className="section-title">Data Freshness & Limitations</h2>
          <div className="limitations-list">
            <div className="limitation-item">
              <Clock size={18} className="limit-icon green" />
              <span>Data is updated every hour</span>
            </div>
            <div className="limitation-item">
              <Calendar size={18} className="limit-icon green" />
              <span>Covers {totalCities} Indian state capitals & UTs</span>
            </div>
            <div className="limitation-item">
              <CheckCircle2 size={18} className="limit-icon green" />
              <span>Uses open data sources (no proprietary data)</span>
            </div>
            <div className="limitation-item">
              <Info size={18} className="limit-icon gray" />
              <span>May have occasional delays due to source availability</span>
            </div>
            <div className="limitation-item">
              <AlertTriangle size={18} className="limit-icon orange" />
              <span>Intended for informational purposes only</span>
            </div>
          </div>
        </div>
      </div>

      <div className="about-footer">
        <div className="footer-left">
          <strong>CityAir Metrics</strong> <span className="separator">|</span> Cleaner Air. Healthier Cities. A Brighter Tomorrow.
        </div>
        <div className="footer-right">
          Open Data <span className="separator">|</span> Open Source <span className="separator">|</span> Built for a Cleaner India <span className="separator">|</span> 
          <a href="#" className="github-link">
             View on GitHub <ExternalLink size={14} />
          </a>
        </div>
      </div>
    </div>
  );
};
