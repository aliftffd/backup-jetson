import React, { useEffect, useState } from 'react';
import { MdOutlineSpeed, MdTrain, MdLocationOn } from 'react-icons/md';
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import GaugeComponent from 'react-gauge-component';
import io from 'socket.io-client';

const MAX_DATA_COUNT = 20;
const MAX_SPEED = 100;
const gaugeLimits = [
  { limit: 20, color: '#5BE12C', showTick: true },
  { limit: 40, color: '#F5CD19', showTick: true },
  { limit: 60, color: '#F58B19', showTick: true },
  { limit: MAX_SPEED, color: '#EA4228', showTick: true },
];

const staticSpeedData = [
  { distance: 10, speed: 100 },
  { distance: 20, speed: 85 },
  { distance: 30, speed: 75 },
  { distance: 40, speed: 65 },
  { distance: 50, speed: 55 },
  { distance: 60, speed: 0 },
];

function Home() {
  const [sensorData, setSensorData] = useState([]);
  const [socketConnected, setSocketConnected] = useState(false);
  const [gaugeValue, setGaugeValue] = useState(0);
  const [distanceData, setDistanceData] = useState([]);

  const kmhToMs = (value) => {
    if (value >= 1) {
      const msValue = value / 3.6;
      return { value: msValue.toFixed(2), unit: 'm/s' };
    } else {
      return { value: value.toFixed(2), unit: 'km/h' };
    }
  };

  const calculateDistance = (data) => {
    let distance = 0;
    const distanceData = data.map((point, index) => {
      if (index === 0) {
        return { ...point, distance };
      }
      const prevPoint = data[index - 1];
      const timeDiff = (new Date(point.date) - new Date(prevPoint.date)) / 1000; // time difference in seconds
      const speedMs = prevPoint.speed / 3.6; // convert speed to m/s
      distance += speedMs * timeDiff; // distance in meters
      return { ...point, distance: distance / 1000 }; // convert to kilometers
    });
    return distanceData;
  };

  useEffect(() => {
    const URL = "http://localhost:5001";
    const socket = io(URL, {
      pinTimeout: 30000,
      pingInterval: 5000,
      upgradeTimeout: 30000,
      cors: {
        origin: "http://localhost:5001",
      }
    });

    socket.connect();
    socket.on("connect_error", (err) => {
      console.log(`connect_error due to ${err.message}`);
    });

    socket.on('connect', () => {
      setSocketConnected(true);
    });

    socket.on('disconnect', () => {
      setSocketConnected(false);
    });

    socket.on('sensorData', ({ value, date }) => {
      setSensorData(prevData => {
        const newData = [...prevData, { date, speed: value }].slice(-MAX_DATA_COUNT);
        setDistanceData(calculateDistance(newData));
        return newData;
      });
      setGaugeValue(value);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const lastSensorData = sensorData.length > 0 ? sensorData[sensorData.length - 1].speed : 0;
  const { value: convertedValue, unit: speedUnit } = kmhToMs(lastSensorData);

  return (
    <main className='main-container'>
      <div className='main-title'>
        <h1>DASHBOARD</h1>
      </div>
      <div className='main-cards'>
        <div className='card'>
          <div className='card-inner'>
            <h3>Speed Rated</h3>
            <MdOutlineSpeed className='card_icon' />
          </div>
          <div className="d-flex align-items-center">
            <h2 id='speedValue'>{convertedValue}</h2>
            <span className="unit">{speedUnit}</span>
          </div>
          <small className="text-muted">Kecepatan yang Terbaca oleh Radar</small>
        </div>
        <div className='card'>
          <div className='card-inner'>
            <h3>Train Position</h3>
            <MdTrain className='card_icon' />
          </div>
          <div className="d-flex align-items-center">
            <h2>33</h2> {/* untuk dihubungkan dengan sensor */}
            <span className="unit">km</span>
          </div>
          <small className="text-muted">Posisi terhadap Jarak</small>
        </div>
        <div className='card'>
          <div className='card-inner'>
            <h3>Blocking</h3>
            <MdLocationOn className='card_icon' />
          </div>
          <div className="d-flex align-items-center">
            <h2>42</h2> {/* untuk dihubungkan dengan sensor */}
          </div>
          <small className="text-muted">Posisi Kereta</small>
        </div>
      </div>
      <div className='charts-wrapper'>
        <div className='line-chart'>
          <ResponsiveContainer width="100%" height="100%">
            <h3>Grafik kecepatan terhadap jarak</h3>
            <LineChart
              width={500}
              height={300}
              data={distanceData}
              margin={{
                top: 5,
                right: 30,
                left: -30,
                bottom: 5,
              }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="distance" label={{ value: "Jarak (km)", position: 'insideBottomRight', offset: 0 }} />
              <YAxis label={{ value: "Kecepatan (m/s)", angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="speed" stroke="#8884d8" activeDot={{ r: 8 }} />
              <Line type="monotone" dataKey="speed" data={staticSpeedData} stroke="green" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className='gauge-chart' style={{ flex: 1, maxWidth: '500px' }}>
          <h3>Gauge Chart</h3>
          <GaugeComponent
            arc={{
              nbSubArcs: gaugeLimits.length,
              colorArray: gaugeLimits.map(limit => limit.color),
              width: 0.3,
              padding: 0.003
            }}
            labels={{
              valueLabel: {
                fontSize: 40,
                formatTextValue: value => kmhToMs(value).value + ' ' + kmhToMs(value).unit
              }
            }}
            value={gaugeValue}
            maxValue={MAX_SPEED}
          />
        </div>
      </div>
    </main>
  );
}

export default Home;
