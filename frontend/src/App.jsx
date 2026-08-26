import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Overview from './pages/Overview';
import BatchOperations from './pages/BatchOperations';
import BatchSubmit from './pages/BatchSubmit';
import PaymentDrillDown from './pages/PaymentDrillDown';
import FailureDemo from './pages/FailureDemo';
import SystemArchitecture from './pages/SystemArchitecture';
import PromiseToPay from './pages/PromiseToPay';
import HinglishRecovery from './pages/HinglishRecovery';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index                        element={<Overview />}          />
          <Route path="batches"               element={<BatchOperations />}   />
          <Route path="batches/:runId"        element={<PaymentDrillDown />}  />
          <Route path="batch-submit"          element={<BatchSubmit />}       />
          <Route path="promise-pay"           element={<PromiseToPay />}      />
          <Route path="hinglish"              element={<HinglishRecovery />}  />
          <Route path="failure-lab"           element={<FailureDemo />}       />
          <Route path="architecture"          element={<SystemArchitecture />}/>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
