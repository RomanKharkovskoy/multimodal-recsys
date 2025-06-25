import React from 'react';
import { Container, Typography, Box, Tabs, Tab, Paper } from '@mui/material';
import BusinessList from './components/BusinessList';
import DataUpload from './components/DataUpload';
import TrainModel from './components/TrainModel';
import Recommendations from './components/Recommendations';
import Metrics from './components/Metrics';
import BusinessIcon from '@mui/icons-material/Business';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import SchoolIcon from '@mui/icons-material/School';
import RecommendIcon from '@mui/icons-material/Recommend';
import AssessmentIcon from '@mui/icons-material/Assessment';

function App() {
  const [tab, setTab] = React.useState(0);

  return (
    <Box sx={{ minHeight: '100vh', background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)', py: 6 }}>
      <Container maxWidth="md">
        <Paper elevation={6} sx={{ borderRadius: 4, p: 4, mt: 2 }}>
          <Typography variant="h3" align="center" gutterBottom sx={{ fontWeight: 700, color: 'primary.main', mb: 3 }}>
            Business Customer Recommender UI
          </Typography>
          <Tabs
            value={tab}
            onChange={(_, v) => setTab(v)}
            centered
            textColor="primary"
            indicatorColor="primary"
            sx={{ mb: 3 }}
          >
            <Tab icon={<BusinessIcon />} label="Бизнесы" />
            <Tab icon={<CloudUploadIcon />} label="Загрузка данных" />
            <Tab icon={<SchoolIcon />} label="Обучение" />
            <Tab icon={<RecommendIcon />} label="Рекомендации" />
            <Tab icon={<AssessmentIcon />} label="Метрики" />
          </Tabs>
          <Box sx={{ mt: 2 }}>
            {tab === 0 && <BusinessList />}
            {tab === 1 && <DataUpload />}
            {tab === 2 && <TrainModel />}
            {tab === 3 && <Recommendations />}
            {tab === 4 && <Metrics />}
          </Box>
        </Paper>
      </Container>
    </Box>
  );
}

export default App;
