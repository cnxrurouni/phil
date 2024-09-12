import DataFetchingComponent from './dataFetcher';

function App() {
  let stocks = DataFetchingComponent();
  console.log(stocks);
  return (
    <>
    <div>Test</div></>
  );
}

export default App;
