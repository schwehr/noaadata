#!/usr/bin/perl

# Written by Robert Aspinall

use LWP::UserAgent;
use HTTP::Request::Common;

my $userAgent = LWP::UserAgent->new(agent => 'perl post');

my $message = "<?xml version=\"1.0\" encoding=\"UTF-8\" ?> 
<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" 
xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" 
xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">

<soapenv:Body>
<water:getWaterLevelRawSixMin 
xmlns:water=\"http://opendap.co-ops.nos.noaa.gov/axis/webservices/waterlevelrawsixmin/wsdl\">
  <stationId xmlns=\"\">8638610</stationId> 
  <beginDate xmlns=\"\">20070122 20:28</beginDate> 
  <endDate xmlns=\"\">20070122 20:58</endDate> 
  <datum xmlns=\"\">MLLW</datum> 
  <unit xmlns=\"\">0</unit> 
  <timeZone xmlns=\"\">0</timeZone> 
  </water:getWaterLevelRawSixMin>
  </soapenv:Body>
  </soapenv:Envelope>
";



my $request = HTTP::Request->new(POST => 'http://opendap.co-ops.nos.noaa.gov/axis/services/WaterLevelRawSixMin');
$request->header(SOAPAction => '"http://opendap.co-ops.nos.noaa.gov/axis/"');
$request->content($message);
$request->content_type("text/xml");

my $response = $userAgent->request($request);

#my $response = $userAgent->request(POST 'http://opendap.co-ops.nos.noaa.gov/axis/services/WaterLevelRawSixMin',
#Content_Type => 'text/xml',
#Content => $message);

print $response->error_as_HTML unless $response->is_success;

print $response->as_string;
