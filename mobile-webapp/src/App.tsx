import Snowfall from 'react-snowfall'
import Jukebox from './components/Jukebox'
import './App.css'

const App = () => {
  return (
    <div className="app">
      <Snowfall
        color={'#dee4fd'}
        snowflakeCount={200}
        radius={[0.5, 3.0]}
        speed={[0.5, 3.0]}
        wind={[-0.5, 2.0]}
        images={undefined}
      />
      <Jukebox />
    </div>
  )
}

export default App
