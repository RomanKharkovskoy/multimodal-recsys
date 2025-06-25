import React, { useState } from 'react';
import axios from 'axios';
import { Box, Button, TextField, Typography, Alert, Paper, Divider, Chip, Stack } from '@mui/material';
import AssessmentIcon from '@mui/icons-material/Assessment';

export default function Metrics() {
  const [businessId, setBusinessId] = useState('');
  const [k, setK] = useState(5);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleGet = async () => {
    setError('');
    setResult(null);
    try {
      const res = await axios.get(`http://localhost:8000/businesses/${businessId}/metrics?k=${k}`);
      setResult(res.data);
    } catch (e) {
      setError('Ошибка получения метрик');
    }
  };

  return (
    <Paper elevation={2} sx={{ p: 3, borderRadius: 3 }}>
      <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>Метрики модели</Typography>
      <Box display="flex" alignItems="center" gap={2}>
        <TextField label="ID бизнеса" value={businessId} onChange={e => setBusinessId(e.target.value)} sx={{ width: 180 }} />
        <TextField label="K" type="number" value={k} onChange={e => setK(Number(e.target.value))} sx={{ width: 80 }} />
        <Button variant="contained" onClick={handleGet} startIcon={<AssessmentIcon />} sx={{ borderRadius: 2 }}>
          Показать
        </Button>
      </Box>
      {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
      {result && (
        <Box sx={{ mt: 3 }}>
          <Divider sx={{ mb: 2 }} />
          <Stack direction="row" spacing={2} flexWrap="wrap">
            {result.precision_at_k !== undefined && (
              <Chip color="primary" label={`Precision@${result.k}: ${result.precision_at_k.toFixed(3)}`} sx={{ fontSize: 16, p: 2 }} />
            )}
            {result.recall_at_k !== undefined && (
              <Chip color="success" label={`Recall@${result.k}: ${result.recall_at_k.toFixed(3)}`} sx={{ fontSize: 16, p: 2 }} />
            )}
            {result.map_at_k !== undefined && (
              <Chip color="info" label={`MAP@${result.k}: ${result.map_at_k.toFixed(3)}`} sx={{ fontSize: 16, p: 2 }} />
            )}
            {result.mrr_at_k !== undefined && (
              <Chip color="secondary" label={`MRR@${result.k}: ${result.mrr_at_k.toFixed(3)}`} sx={{ fontSize: 16, p: 2 }} />
            )}
            {result.diversity_at_k !== undefined && (
              <Chip color="warning" label={`Diversity@${result.k}: ${result.diversity_at_k.toFixed(3)}`} sx={{ fontSize: 16, p: 2 }} />
            )}
          </Stack>
        </Box>
      )}
    </Paper>
  );
}
