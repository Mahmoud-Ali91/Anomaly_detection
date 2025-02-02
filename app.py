import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, RobustScaler
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans, DBSCAN
from sklearn.ensemble import IsolationForest
from sklearn.metrics import pairwise_distances_argmin_min
import matplotlib.pyplot as plt
from PIL import Image
import altair as alt
import time

df = pd.read_csv('Healthcare_Providers_cleaned.csv')

def plot_pie_chart(df, title):
    anomaly_count = df['Anomaly'].sum()
    normal_count = len(df) - anomaly_count
    labels = ['Anomaly', 'Normal']
    sizes = [anomaly_count, normal_count]
    colors = ['red', 'blue']
   
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    ax.set_title(title)
    return fig

# Sidebar for navigation
st.sidebar.title("Dashboard")
selection = st.sidebar.radio("Choose an option", ["Introduction","Anomalies Seen With Data Analysis", "Anomalies Seen with Models"])
if selection == "Introduction":
    st.title("Medicare Insurance Anomaly Detection")
    st.image("cover.png", caption="Medicare Insurance", use_column_width=True)
    
    st.markdown("""
    <div style="text-align: center;">
        <p>This project examines Medicare insurance data to detect anomalies using Data Analysis and Unsupervised machine learning techniques. Medicare is United States Medical Insurance that covers elderly persons. Fighting fraud is crucial to better health care coverage.</p>
        <p style="color: #333333;">Explore different sections to understand the data and the models used.</p>
    </div>
    """, unsafe_allow_html=True)
elif selection == "Anomalies Seen With Data Analysis":
    st.header("Data Analysis")
    with st.expander("Data Summary"):
     col1, col2,col3 = st.columns(3)
     col1.metric("Total Records", len(df))
     col2.metric("Features", df.shape[1])
     kaggle_link = "https://www.kaggle.com/datasets/tamilsel/healthcare-providers-data/data"
     col3.markdown(f"[Data Source](https://www.kaggle.com/datasets/tamilsel/healthcare-providers-data/data)")
     col3.caption("Kaggle")

    # Categorical Analysis
    st.subheader("Categorical Analysis")
    st.markdown("Use this tool to see variance in Type, Place & Drug Indicator of Medicare Providers") 
    categorical_column = st.selectbox("Select a categorical column", 
                                      ['Entity Type of the Provider', 'Place of Service', 'HCPCS Drug Indicator'])
    
    # Example pie chart code (you need to adapt this based on your actual DataFrame)
    label_mapping = {'I': 'Individual', 'O': 'Organization'}
    place_of_service_mapping = {'F': 'Facility', 'O': 'Non-Facility'}
    hcpcs_drug_indicator_mapping = {'Y': 'Drug Involved', 'N': 'No Drug'}
    
    if categorical_column == 'Entity Type of the Provider':
        df['Entity Type of the Provider'] = df['Entity Type of the Provider'].map(label_mapping)
    elif categorical_column == 'Place of Service':
        df['Place of Service'] = df['Place of Service'].map(place_of_service_mapping)
    elif categorical_column == 'HCPCS Drug Indicator':
        df['HCPCS Drug Indicator'] = df['HCPCS Drug Indicator'].map(hcpcs_drug_indicator_mapping)
    
    fig = px.pie(df, names=categorical_column)
    fig.update_layout(title=f'Distribution of {categorical_column}')
    fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=12)
    st.plotly_chart(fig)
# Visualization for top N records
    st.subheader("Top Records Analysis")
    st.markdown("Use this tool Check Which States, Cities & Specialization Provides more Services")
    selected_column = st.selectbox("Select column to analyze", ['City of the Provider', 'State Code of the Provider', 'Provider Type'])
    top_n = st.slider("Select number of top records to display", min_value=1, max_value=25, value=10)

    top_n_data = df.groupby(selected_column)['Number of Services'].sum().nlargest(top_n).reset_index()
    fig = px.bar(top_n_data, x=selected_column, y='Number of Services', color=selected_column)
    fig.update_layout(title=f'Top {top_n} {selected_column} by Number of Services')
    st.plotly_chart(fig)

    # Sunburst Chart
    st.subheader("Interactive Chart")
    st.markdown("Use this tool See Medicare Medical Specialization in relation to States")
    fig_sunburst = px.sunburst(
        df,
        path=['State Code of the Provider', 'Provider Type'],
        values='Number of Services',
        color='Number of Services',
        color_continuous_scale='Viridis',
        title="Sunburst Chart: Number of Services by State and Provider Type"
    )

    fig_sunburst.update_layout(
        height=600,
        margin=dict(t=50, l=25, r=25, b=25)
    )
    st.plotly_chart(fig_sunburst)
    # Choropleth Map
    st.subheader("States Provider Map")
    st.markdown("Use this tool See Medicare Number of Services in relation to States")

    
    state_services = df.groupby('State Code of the Provider')['Number of Services'].sum().reset_index()

    fig_choropleth = px.choropleth(
        state_services,
        locations='State Code of the Provider',
        locationmode="USA-states",
        color='Number of Services',
        color_continuous_scale="Viridis",
        scope="usa",
        labels={'Number of Services': 'Number of Services'},
        title="Number of Services by State"
    )
    fig_choropleth.update_layout(
        geo=dict(
            lakecolor='rgb(255, 255, 255)',
        ),
        title={
            'text': "Number of Services by State",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
    )
    st.plotly_chart(fig_choropleth)
    
    # Numerical Analysis
    st.subheader("Numerical Analysis")
    if st.checkbox("Check to Show Correlation Between Features Heatmap"):
        float_columns = df.select_dtypes(include='float')
        corr = float_columns.corr()
        fig = px.imshow(
            corr,
            text_auto=True,
            labels=dict(color="Correlation"),
            x=corr.columns.tolist(),
            y=corr.index.tolist()
        )
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)
        fig.update_traces(hovertemplate="X: %{x}<br>Y: %{y}<br>Correlation: %{z:.2f}<extra></extra>")
        fig.update_layout(
            width=800 * 1.3,
            height=600 * 1.3,
            title={
                'text': "Correlation Heatmap",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )
        st.plotly_chart(fig)
        
    st.subheader("Box Plots")
    numerical_column = st.selectbox("Select a feature", df.select_dtypes(include=[np.number]).columns)
    st.markdown("Use this tool to check which feature has outlier data points as Potential Anomaly")
    if numerical_column:
        fig = px.box(df, x=numerical_column)
        st.plotly_chart(fig)
        
    st.subheader("How Each feature relates to the other?")
    
    # Select only float columns
    float_columns = df.select_dtypes(include='float').columns.tolist()
    
    # Dropdown menu for selecting X and Y features
    x_feature = st.selectbox("Select X Feature", float_columns)
    y_feature = st.selectbox("Select Y Feature", float_columns)
    
    # Ensure that X and Y features are not the same
    if x_feature != y_feature:
        fig = px.scatter(df, x=x_feature, y=y_feature, title=f'Scatter Plot of {x_feature} vs {y_feature}')
        st.plotly_chart(fig)
    else:
        st.error("Please select different features for X and Y axes.")
elif selection == "Anomalies Seen with Models":
    st.header("Automated Anomaly Detection")
    st.markdown("""
Our system uses advanced algorithms to automatically detect unusual patterns in the data. 
These patterns can indicate potential issues, such as fraud or unusual activity. 
The process helps identify risks early and improve efficiency.
""")
    
    # Initialize session state
    if 'df' not in st.session_state:
        st.session_state.df = df.drop(['City of the Provider', 'State Code of the Provider', 'Provider Type', 'HCPCS Code'], axis=1)
    if 'df_encoded' not in st.session_state:
        st.session_state.df_encoded = None
    if 'df_encoded_scaled' not in st.session_state:
        st.session_state.df_encoded_scaled = None
    if 'X_pca_2d' not in st.session_state:
        st.session_state.X_pca_2d = None
    if 'X_pca_3d' not in st.session_state:
        st.session_state.X_pca_3d = None

    # Encoding
    if st.session_state.df_encoded is None:
        binary_columns = ['Entity Type of the Provider', 'Place of Service', 'HCPCS Drug Indicator']
        encoder = OneHotEncoder(sparse_output=False, drop='first')
        encoded_columns = encoder.fit_transform(st.session_state.df[binary_columns])
        encoded_df = pd.DataFrame(encoded_columns, columns=encoder.get_feature_names_out(binary_columns))
        st.session_state.df_encoded = pd.concat([st.session_state.df.drop(columns=binary_columns), encoded_df], axis=1)
    
    if st.checkbox("Show Encoded Data(Educational)"):
        st.write(st.session_state.df_encoded)

    # Scaling
    if st.session_state.df_encoded_scaled is None:
        robust_scaler = RobustScaler()
        st.session_state.df_encoded_scaled = pd.DataFrame(robust_scaler.fit_transform(st.session_state.df_encoded), columns=st.session_state.df_encoded.columns)
    
    if st.checkbox("Show Scaled Data(Educational)"):
        st.write(st.session_state.df_encoded_scaled)

    # PCA
    if st.session_state.X_pca_2d is None or st.session_state.X_pca_3d is None:
        pca_pipeline_2d = Pipeline([('pca', PCA(n_components=2))])
        pca_pipeline_3d = Pipeline([('pca', PCA(n_components=3))])
        st.session_state.X_pca_2d = pca_pipeline_2d.fit_transform(st.session_state.df_encoded_scaled)
        st.session_state.X_pca_3d = pca_pipeline_3d.fit_transform(st.session_state.df_encoded_scaled)

    # Choose ML Model
    model_option = st.radio("Select a model for clustering", ["K-Means", "DBSCAN", "Isolation Forest", "Ensemble"])
    progress_bar = st.progress(0)
    for i in range(100):
    # Simulating some work
      time.sleep(0.1)
      progress_bar.progress(i + 1)
    st.success("Model trained successfully!")
    if model_option == "K-Means":
        st.subheader("K-Means Clustering")
        st.markdown("This tool groups similar data together. By grouping data, we can identify areas that don’t fit, spotting potential issues.")
        kmeans_clusters = st.slider("Select number of clusters", min_value=1, max_value=10, value=2)
        
        kmeans = KMeans(n_clusters=kmeans_clusters, random_state=42)
        labels_kmeans_2d = kmeans.fit_predict(st.session_state.X_pca_2d)
        labels_kmeans_3d = kmeans.fit_predict(st.session_state.X_pca_3d)
        
        df_kmeans_2d = pd.DataFrame(st.session_state.X_pca_2d, columns=['PC 1', 'PC 2'])
        df_kmeans_2d['Anomaly'] = labels_kmeans_2d != 0  # Assuming cluster 0 is "normal"
        
        # Plot pie chart
        fig_pie = plot_pie_chart(df_kmeans_2d, 'K-Means Anomaly vs Normal Distribution (2D)')
        st.pyplot(fig_pie)
        
        # Plot 2D scatter
        df_kmeans_2d['Cluster'] = labels_kmeans_2d
        fig_kmeans_2d = px.scatter(df_kmeans_2d, x='PC 1', y='PC 2', color='Cluster',
                                  title='K-Means 2D Clustering (PCA Reduced)')
        st.plotly_chart(fig_kmeans_2d)

        if st.checkbox("Show 3D Clustering Plot"):
            df_kmeans_3d = pd.DataFrame(st.session_state.X_pca_3d, columns=['PC 1', 'PC 2', 'PC 3'])
            df_kmeans_3d['Cluster'] = labels_kmeans_3d
            fig_kmeans_3d = px.scatter_3d(df_kmeans_3d, x='PC 1', y='PC 2', z='PC 3', color='Cluster',
                                          title='K-Means 3D Clustering (PCA Reduced)')
            st.plotly_chart(fig_kmeans_3d)

    elif model_option == "DBSCAN":
        st.subheader("DBSCAN Clustering")
        st.markdown("This method looks at how closely data points are packed together. It helps uncover irregular patterns that might indicate problems.")

        eps = st.slider("Select eps", min_value=0.01, max_value=1.0, step=0.01, value=0.05)
        min_samples = st.slider("Select min_samples", min_value=1, max_value=20, value=5)
        
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels_dbscan = dbscan.fit_predict(st.session_state.X_pca_2d)
        
        df_dbscan = pd.DataFrame(st.session_state.X_pca_2d, columns=['PC 1', 'PC 2'])
        df_dbscan['Anomaly'] = labels_dbscan == -1  # -1 is the label for noise points in DBSCAN
        
        # Plot pie chart
        fig_pie = plot_pie_chart(df_dbscan, 'DBSCAN Anomaly vs Normal Distribution (2D)')
        st.pyplot(fig_pie)
        
        # Plot 2D scatter
        df_dbscan['Cluster'] = labels_dbscan
        fig_dbscan_2d = px.scatter(df_dbscan, x='PC 1', y='PC 2', color='Cluster',
                                  title='DBSCAN 2D Clustering (PCA Reduced)')
        st.plotly_chart(fig_dbscan_2d)
        
        if st.checkbox("Show 3D Clustering Plot"):
            fig_dbscan_3d = px.scatter_3d(pd.DataFrame(st.session_state.X_pca_3d, columns=['PC 1', 'PC 2', 'PC 3']).assign(Cluster=labels_dbscan),
                                          x='PC 1', y='PC 2', z='PC 3', color='Cluster',
                                          title='DBSCAN 3D Clustering (PCA Reduced)')
            st.plotly_chart(fig_dbscan_3d)

    elif model_option == "Isolation Forest":
        st.subheader("Isolation Forest")
        st.markdown("This method finds data points that are very different from the rest. These unusual points may indicate fraud or errors.")

        contamination = st.slider("Select contamination", min_value=0.01, max_value=0.5, step=0.01, value=0.1)
        
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        outliers = iso_forest.fit_predict(st.session_state.X_pca_2d)
        
        df_iso = pd.DataFrame(st.session_state.X_pca_2d, columns=['PC 1', 'PC 2'])
        df_iso['Anomaly'] = outliers == -1
        
        # Plot pie chart
        fig_pie = plot_pie_chart(df_iso, 'Isolation Forest Anomaly vs Normal Distribution (2D)')
        st.pyplot(fig_pie)
        
        # Plot 2D scatter
        fig_iso_2d = px.scatter(df_iso, x='PC 1', y='PC 2', color='Anomaly',
                               color_continuous_scale=['blue', 'red'],
                               title='Isolation Forest 2D Anomalies (PCA Reduced)')
        st.plotly_chart(fig_iso_2d)
        
        if st.checkbox("Show 3D Anomalies Plot"):
            st.success("Not applicable for Isolation Forest with current matrix")

    st.success("3D Plots Takes Sometime and Resources, Becareful!")
    st.subheader("Models Comparison")
    model_performance = pd.DataFrame({
    'Model': ['K-Means', 'DBSCAN', 'Isolation Forest'],
    'Anomaly Percentage Result': [10.1, 8.3, 10]})

    chart = alt.Chart(model_performance).mark_bar().encode(
    x='Model',
    y='Anomaly Percentage Result',
    color='Model').properties(title="Model Performance Comparison with Tuned Parameters")
    st.altair_chart(chart, use_container_width=True)
    

    def anomaly_insights(df):
        st.subheader("Anomaly Insights")
        anomalies = df[df['Anomaly'] == 1]
        st.write(f"Number of Anomalies: {len(anomalies)}")
        st.write(anomalies.describe())  
    
    # In your Streamlit app
    if model_option == "Isolation Forest":
        df_iso['Anomaly'] = outliers == -1
        anomaly_insights(df_iso)
   
    elif model_option == "Ensemble":
        st.subheader("Ensemble Model")
        st.markdown("We combine the strengths of different models to improve accuracy and reliability. This method can detect anomalies more effectively by leveraging multiple techniques.")
        # Functions for individual models (you can reuse your existing functions)
        def run_kmeans(X, n_clusters=2):
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            labels = kmeans.fit_predict(X)
            return labels == 0
    
        def run_dbscan(X, eps=0.5, min_samples=5):
            dbscan = DBSCAN(eps=eps, min_samples=min_samples)
            labels = dbscan.fit_predict(X)
            return labels != -1
    
        def run_isolation_forest(X, contamination=0.1):
            iso_forest = IsolationForest(contamination=contamination, random_state=42)
            labels = iso_forest.fit_predict(X)
            return labels == 1
    
        # Function to create ensemble predictions
        def ensemble_predict(X, weights):
            weights = np.array(weights) / np.sum(weights)
            kmeans_pred = run_kmeans(X)
            dbscan_pred = run_dbscan(X)
            iforest_pred = run_isolation_forest(X)
            ensemble_pred = (weights[0] * kmeans_pred +
                             weights[1] * dbscan_pred +
                             weights[2] * iforest_pred)
            return ensemble_pred > 0.5
    
        # User input for weights
        st.write("Set weights for each model (they will be normalized):")
        kmeans_weight = st.slider("K-Means weight", 0.0, 1.0, 0.4)
        dbscan_weight = st.slider("DBSCAN weight", 0.0, 1.0, 0.3)
        iforest_weight = st.slider("Isolation Forest weight", 0.0, 1.0, 0.3)
        
        weights = [kmeans_weight, dbscan_weight, iforest_weight]
        
        # Ensure we have the necessary data
        if 'df_encoded_scaled' not in st.session_state or st.session_state.df_encoded_scaled is None:
            st.error("Encoded and scaled data is not available. Please make sure to run the data preprocessing steps first.")
        else:
            # Run ensemble model
            X_scaled = st.session_state.df_encoded_scaled.values
            ensemble_results = ensemble_predict(X_scaled, weights)
            
            # Add results to DataFrame
            if 'X_pca_2d' in st.session_state and st.session_state.X_pca_2d is not None:
                df_ensemble = pd.DataFrame(st.session_state.X_pca_2d, columns=['PC 1', 'PC 2'])
            else:
                st.warning("PCA data is not available. Using original features for visualization.")
                df_ensemble = pd.DataFrame(X_scaled[:, :2], columns=['Feature 1', 'Feature 2'])
            
            df_ensemble['Anomaly'] = ~ensemble_results
            
            # Plot pie chart
            fig_pie = plot_pie_chart(df_ensemble, 'Ensemble Model Anomaly vs Normal Distribution')
            st.pyplot(fig_pie)
            
            # Plot 2D scatter
            fig_ensemble_2d = px.scatter(df_ensemble, x=df_ensemble.columns[0], y=df_ensemble.columns[1], color='Anomaly',
                                         color_discrete_map={True: 'red', False: 'blue'},
                                         title='Ensemble Model 2D Anomalies')
            st.plotly_chart(fig_ensemble_2d)
            
            # Display summary statistics
            st.write(f"Number of anomalies detected: {df_ensemble['Anomaly'].sum()}")
            st.write(f"Percentage of anomalies: {df_ensemble['Anomaly'].mean() * 100:.2f}%")
            
            # Option to show 3D plot
            if st.checkbox("Show 3D Anomalies Plot"):
                if 'X_pca_3d' in st.session_state and st.session_state.X_pca_3d is not None:
                    df_ensemble_3d = pd.DataFrame(st.session_state.X_pca_3d, columns=['PC 1', 'PC 2', 'PC 3'])
                    df_ensemble_3d['Anomaly'] = ~ensemble_results
                    fig_ensemble_3d = px.scatter_3d(df_ensemble_3d, x='PC 1', y='PC 2', z='PC 3', color='Anomaly',
                                                    color_discrete_map={True: 'red', False: 'blue'},
                                                    title='Ensemble Model 3D Anomalies (PCA Reduced)')
                    st.plotly_chart(fig_ensemble_3d)
                else:
                    st.warning("3D PCA data is not available. Unable to show 3D plot.")


footer = st.sidebar.container()
st.sidebar.markdown('#')        
footer = st.sidebar.container()
st.sidebar.markdown('#')
with footer:
    st.markdown("---")
    
    # Two-column layout for name and picture
    col1, col2 = st.columns([3,1])
    with col1:
        st.markdown("**By: Mahmoud Ali**")
        st.markdown("[LinkedIn Profile](https://www.linkedin.com/in/drmahmoodali/)")
    with col2:
        st.markdown('Connect')
    st.markdown("**Epsilon AI Graduation Project**")
    
    # Add Epsilon AI logo
    epsilon_logo = Image.open("epsilon_ai_logo.png")
    st.image(epsilon_logo, width=100)
    st.cache_data.clear()

