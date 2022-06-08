const el = document.getElementById('container');
const form = document.getElementById('fileform');
const btn = document.getElementById('submit');

btn.addEventListener('click', function submit() {
  form.contentEditable = false;
    form.style.display = 'none';
    el.style.display = 'block';
});


function tableToCSV() {
  var csv_data = [];

  // get each row data
  var rows = document.getElementsByTagName('tr')
  for (var i=0; i < rows.length; i++) {

    // get colunms
    var cols = rows[i].querySelectorAll('td,th');

    // store each csv row
    var csvrow = [];
    for (var j=0; j < cols.length; j++) {
      csvrow.push(cols[j].innerHTML);
    }
    // combine with commas
    csv_data.push(csvrow.join(","));
  }
  csv_data = csv_data.join('\n');
  downloadCSV(csv_data);
}


function downloadCSV (csv_data) {
  // create csv file and add data
  CSVFile = new Blob([csv_data], {type:"text/csv"});
  // make temp link
  var temp_link = document.createElement('a');
  // download csv
  temp_link.download = 'CSF.csv';
  var url = window.URL.createObjectURL(CSVFile);
  temp_link.href = url;
  // hide link
  temp_link.style.display = 'none';
  document.body.appendChild(temp_link);
  // automatically click link
  temp_link.click();
  document.body.removeChild(temp_link);
}