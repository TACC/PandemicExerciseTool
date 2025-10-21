import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class VisualizationGenerator:
    """Handles creation of visualizations for the pandemic simulation"""
    
    def __init__(self, data_loader):
        self.data_loader = data_loader
        
    def create_choropleth_map(self, event_data: List[Dict], timeline_value: int, 
                            view_type: str = 'percent') -> go.Figure:
        """Create a choropleth map of Texas counties"""
        
        if not event_data or timeline_value >= len(event_data):
            return self._create_empty_map()
        
        current_data = event_data[timeline_value]
        counties_data = current_data.get('counties', [])
        
        if not counties_data:
            return self._create_empty_map()
        
        # Prepare data for choropleth
        fips_codes = []
        values = []
        hover_text = []
        
        for county in counties_data:
            fips = county.get('fips', '')
            county_name = self.data_loader.get_county_name_by_fips(fips)
            
            if view_type == 'percent':
                infected_val = county.get('infectedPercent', 0)
                deceased_val = county.get('deceasedPercent', 0)
                hover_text.append(f"{county_name}<br>Infected: {infected_val:.1f}%<br>Deceased: {deceased_val:.1f}%")
            else:
                infected_val = county.get('infected', 0)
                deceased_val = county.get('deceased', 0)
                hover_text.append(f"{county_name}<br>Infected: {infected_val:,}<br>Deceased: {deceased_val:,}")
            
            fips_codes.append(fips)
            values.append(infected_val)
        
        # Create choropleth map
        fig = go.Figure(data=go.Choropleth(
            locations=fips_codes,
            z=values,
            locationmode='geojson-id',
            colorscale='Reds',
            text=hover_text,
            hovertemplate='%{text}<extra></extra>',
            colorbar=dict(
                title=f"Infected ({'%' if view_type == 'percent' else 'Count'})",
                thickness=15,
                len=0.7
            )
        ))
        
        # Try to load Texas GeoJSON if available
        try:
            texas_geojson = self.data_loader.load_texas_mapping()
            fig.update_traces(geojson=texas_geojson)
        except:
            # Fallback to state-level choropleth
            fig.update_traces(
                locations=['TX'] * len(fips_codes),
                locationmode='USA-states'
            )
        
        fig.update_layout(
            title=f"Day {current_data['day']} - Texas Counties ({'Percentage' if view_type == 'percent' else 'Count'} View)",
            geo=dict(
                scope='usa',
                projection=go.layout.geo.Projection(type='albers usa'),
                showlakes=True,
                lakecolor='rgb(255, 255, 255)',
                center=dict(lat=31.0, lon=-99.0),  # Center on Texas
                lonaxis_range=[-106.0, -93.0],
                lataxis_range=[25.0, 37.0]
            ),
            height=400,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        return fig
    
    def create_line_chart(self, event_data: List[Dict], npi_data: Optional[List] = None) -> go.Figure:
        """Create epidemic curve line chart"""
        
        if not event_data:
            return self._create_empty_line_chart()
        
        days = [d['day'] for d in event_data]
        
        # Extract compartment data
        susceptible = [d.get('totalSusceptible', 0) for d in event_data]
        exposed = [d.get('totalExposed', 0) for d in event_data]
        asymptomatic = [d.get('totalAsymptomaticCount', 0) for d in event_data]
        treatable = [d.get('totalTreatableCount', 0) for d in event_data]
        infected = [d.get('totalInfectedCount', 0) for d in event_data]
        recovered = [d.get('totalRecoveredCount', 0) for d in event_data]
        deceased = [d.get('totalDeceased', 0) for d in event_data]
        
        fig = go.Figure()
        
        # Add traces for each compartment
        fig.add_trace(go.Scatter(
            x=days, y=susceptible, name='Susceptible',
            line=dict(color='blue', width=2),
            hovertemplate='Day %{x}<br>Susceptible: %{y:,}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=days, y=exposed, name='Exposed',
            line=dict(color='orange', width=2),
            hovertemplate='Day %{x}<br>Exposed: %{y:,}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=days, y=asymptomatic, name='Asymptomatic',
            line=dict(color='yellow', width=2),
            hovertemplate='Day %{x}<br>Asymptomatic: %{y:,}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=days, y=treatable, name='Treatable',
            line=dict(color='purple', width=2),
            hovertemplate='Day %{x}<br>Treatable: %{y:,}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=days, y=infected, name='Infected',
            line=dict(color='red', width=3),
            hovertemplate='Day %{x}<br>Infected: %{y:,}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=days, y=recovered, name='Recovered',
            line=dict(color='green', width=2),
            hovertemplate='Day %{x}<br>Recovered: %{y:,}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=days, y=deceased, name='Deceased',
            line=dict(color='black', width=2),
            hovertemplate='Day %{x}<br>Deceased: %{y:,}<extra></extra>'
        ))
        
        # Add NPI indicators if available
        if npi_data:
            for npi in npi_data:
                start_day = npi.get('start_day', 0)
                if start_day <= max(days):
                    fig.add_vline(
                        x=start_day,
                        line_dash="dash",
                        line_color="gray",
                        annotation_text=f"NPI: {npi.get('type', 'Unknown')}",
                        annotation_position="top"
                    )
        
        fig.update_layout(
            title="Epidemic Curve - SEATIRD Model",
            xaxis_title="Day",
            yaxis_title="Population Count",
            height=300,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=40, r=40, t=60, b=40),
            hovermode='x unified'
        )
        
        return fig
    
    def create_summary_table(self, event_data: List[Dict], timeline_value: int, 
                           view_type: str = 'percent', sort_config: Dict = None) -> pd.DataFrame:
        """Create summary table data"""
        
        if not event_data or timeline_value >= len(event_data):
            return pd.DataFrame()
        
        current_data = event_data[timeline_value]
        counties_data = current_data.get('counties', [])
        
        if not counties_data:
            return pd.DataFrame()
        
        # Prepare table data
        table_data = []
        for county in counties_data:
            fips = county.get('fips', '')
            county_name = self.data_loader.get_county_name_by_fips(fips)
            
            if view_type == 'percent':
                infected_val = f"{county.get('infectedPercent', 0):.1f}%"
                deceased_val = f"{county.get('deceasedPercent', 0):.1f}%"
                infected_sort = county.get('infectedPercent', 0)
                deceased_sort = county.get('deceasedPercent', 0)
            else:
                infected_val = f"{county.get('infected', 0):,}"
                deceased_val = f"{county.get('deceased', 0):,}"
                infected_sort = county.get('infected', 0)
                deceased_sort = county.get('deceased', 0)
            
            table_data.append({
                'County': county_name,
                'FIPS': fips,
                'Infected': infected_val,
                'Deceased': deceased_val,
                'InfectedSort': infected_sort,
                'DeceasedSort': deceased_sort
            })
        
        df = pd.DataFrame(table_data)
        
        # Apply sorting if specified
        if sort_config and len(df) > 0:
            sort_column = sort_config.get('category', 'County')
            sort_order = sort_config.get('order', 'asc')
            ascending = sort_order == 'asc'
            
            if sort_column == 'county':
                df = df.sort_values('County', ascending=ascending)
            elif sort_column == 'infected':
                df = df.sort_values('InfectedSort', ascending=ascending)
            elif sort_column == 'deceased':
                df = df.sort_values('DeceasedSort', ascending=ascending)
        
        # Remove sort columns
        df = df.drop(columns=['InfectedSort', 'DeceasedSort'], errors='ignore')
        
        return df
    
    def _create_empty_map(self) -> go.Figure:
        """Create empty map figure"""
        fig = go.Figure()
        fig.update_layout(
            title="Texas Counties - No Data Available",
            geo=dict(
                scope='usa',
                projection=go.layout.geo.Projection(type='albers usa'),
                showlakes=True,
                lakecolor='rgb(255, 255, 255)',
                center=dict(lat=31.0, lon=-99.0),
                lonaxis_range=[-106.0, -93.0],
                lataxis_range=[25.0, 37.0]
            ),
            height=400,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        return fig
    
    def _create_empty_line_chart(self) -> go.Figure:
        """Create empty line chart figure"""
        fig = go.Figure()
        fig.update_layout(
            title="Epidemic Curve - No Data Available",
            xaxis_title="Day",
            yaxis_title="Population Count",
            height=300,
            margin=dict(l=40, r=40, t=60, b=40)
        )
        return fig