import React, { useState } from 'react';
import axios from 'axios';
import { Box, Button, TextField, Typography, Checkbox, FormControlLabel, Alert, Paper } from '@mui/material';
import SchoolIcon from '@mui/icons-material/School';

export default function TrainModel() {
  const [businessId, setBusinessId] = useState('');
  const [nSamples, setNSamples] = useState(50);
  const [useTabular, setUseTabular] = useState(true);
  const [useText, setUseText] = useState(true);
  const [status, setStatus] = useState('');

  const handleTrain = async () => {
    try {
      await axios.post(`http://localhost:8000/businesses/${businessId}/train`, {
        n_samples: nSamples,
        use_tabular: useTabular,
        use_text: useText
      });
      setStatus('Модель успешно обучена!');
    } catch (e) {
      setStatus('Ошибка обучения модели');
    }
  };

  return (
    <Paper elevation={2} sx={{ p: 3, borderRadius: 3 }}>
      <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>Обучение модели</Typography>
      <Box display="flex" alignItems="center" gap={2}>
        <TextField label="ID бизнеса" value={businessId} onChange={e => setBusinessId(e.target.value)} sx={{ width: 180 }} />
        <TextField label="Кол-во примеров" type="number" value={nSamples} onChange={e => setNSamples(Number(e.target.value))} sx={{ width: 160 }} />
        <FormControlLabel control={<Checkbox checked={useTabular} onChange={e => setUseTabular(e.target.checked)} />} label="Табличные" />
        <FormControlLabel control={<Checkbox checked={useText} onChange={e => setUseText(e.target.checked)} />} label="Текстовые" />
        <Button variant="contained" onClick={handleTrain} startIcon={<SchoolIcon />} sx={{ borderRadius: 2 }}>
          Обучить
        </Button>
      </Box>
      {status && <Alert severity={status.includes('успешно') ? 'success' : 'error'} sx={{ mt: 2 }}>{status}</Alert>}
    </Paper>
  );
}
