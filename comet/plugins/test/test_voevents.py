import shutil
import tempfile
import textwrap
from contextlib import contextmanager
from functools import partial
import lxml.etree as etree
from comet.protocol.messages import authenticateresponse


DUMMY_VOEVENT_INTEGRAL = u"""
<?xml version='1.0' encoding='UTF-8'?>
<voe:VOEvent xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0" xsi:schemaLocation="http://www.ivoa.net/xml/VOEvent/v2.0 http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd" version="2.0" role="test" ivorn="INTEGRAL/dummy/demo#1">
  <Who>
    <Description>VOEvent created with voevent-parse, version 1.0.3. See https://github.com/timstaley/voevent-parse for details.</Description>
    <AuthorIVORN>ivo://INTEGRAL/dummy_demo</AuthorIVORN>
    <Date>2022-05-20T11:10:32</Date>
    <Author>
      <contactName>James Rodi</contactName>
      <title>Hotwired VOEvent Hands-on</title>
    </Author>
  </Who>
  <What>
    <Param ucd="phot.mag" value="18.77" name="mag" dataType="float"/>
    <Group name="historic">
      <Param ucd="phot.mag" value="19.62" name="hist_mag" dataType="float"/>
      <Param ucd="phot.mag" value="0.07" name="hist_scatter" dataType="float"/>
    </Group>
    <Param ucd="phot.mag" value="18.77" name="mag" dataType="float"/>
    <Group name="historic">
      <Param ucd="phot.mag" value="19.62" name="hist_mag" dataType="float"/>
      <Param ucd="phot.mag" value="0.07" name="hist_scatter" dataType="float"/>
    </Group>
  </What>
  <WhereWhen>
    <ObsDataLocation>
      <ObservatoryLocation id="INTEGRAL"/>
      <ObservationLocation>
        <AstroCoordSystem id="UTC-FK5-GEO"/>
        <AstroCoords coord_system_id="UTC-FK5-GEO">
          <Time unit="s">
            <TimeInstant>
              <ISOTime>2022-05-09T08:07:00</ISOTime>
            </TimeInstant>
          </Time>
          <Position2D unit="deg">
            <Name1>RA</Name1>
            <Name2>Dec</Name2>
            <Value2>
              <C1>314.6578836056712</C1>
              <C2>12.45</C2>
            </Value2>
            <Error2Radius>0</Error2Radius>
          </Position2D>
        </AstroCoords>
      </ObservationLocation>
    </ObsDataLocation>
  </WhereWhen>
  <Description>This is not an official INTEGRAL data product.</Description>
</voe:VOEvent>"""
DUMMY_VOEVENT_INTEGRAL = textwrap.dedent(DUMMY_VOEVENT_INTEGRAL).strip().encode('UTF-8')


DUMMY_VOEVENT_AGILE = u"""
<?xml version='1.0' encoding='UTF-8'?>
<voe:VOEvent xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0" xsi:schemaLocation="http://www.ivoa.net/xml/VOEvent/v2.0 http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd" version="2.0" role="test" ivorn="ivo://dummy.txt#1">
  <Who>
    <Description>VOEvent created with voevent-parse, version 1.0.3. See https://github.com/timstaley/voevent-parse for details.</Description>
    <AuthorIVORN>ivo://AGILE_MCAL_TRIGGER/</AuthorIVORN>
    <Date>2022-05-30T11:10:32</Date>
    <Author>
      <contactName>Andrea Bulgarelli</contactName>
      <title>Hotwired VOEvent Hands-on</title>
    </Author>
  </Who>
  <What>
    <Param ucd="phot.mag" value="18.77" name="mag" dataType="float"/>
    <Group name="historic">
      <Param ucd="phot.mag" value="19.62" name="hist_mag" dataType="float"/>
      <Param ucd="phot.mag" value="0.07" name="hist_scatter" dataType="float"/>
    </Group>
    <Param ucd="phot.mag" value="18.77" name="mag" dataType="float"/>
    <Group name="historic">
      <Param ucd="phot.mag" value="19.62" name="hist_mag" dataType="float"/>
      <Param ucd="phot.mag" value="0.07" name="hist_scatter" dataType="float"/>
    </Group>
  </What>
  <WhereWhen>
    <ObsDataLocation>
      <ObservatoryLocation id="AGILE"/>
      <ObservationLocation>
        <AstroCoordSystem id="UTC-FK5-GEO"/>
        <AstroCoords coord_system_id="UTC-FK5-GEO">
          <Time unit="s">
            <TimeInstant>
              <ISOTime>2022-05-30T11:10:32</ISOTime>
            </TimeInstant>
          </Time>
          <Position2D unit="deg">
            <Name1>RA</Name1>
            <Name2>Dec</Name2>
            <Value2>
              <C1>0.0</C1>
              <C2>0.0</C2>
            </Value2>
            <Error2Radius>0</Error2Radius>
          </Position2D>
        </AstroCoords>
      </ObservationLocation>
    </ObsDataLocation>
  </WhereWhen>
  <Description>This is not an official AGILE data product.</Description>
</voe:VOEvent>"""
DUMMY_VOEVENT_AGILE = textwrap.dedent(DUMMY_VOEVENT_AGILE).strip().encode('UTF-8')


DUMMY_VOEVENT_CHIME = u"""
<?xml version='1.0' encoding='UTF-8'?>
<voe:VOEvent xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0" xsi:schemaLocation="http://www.ivoa.net/xml/VOEvent/v2.0 http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd" version="2.0" role="observation" ivorn="ivo://ca.chimenet.frb/FRB-DETECTION-#2022-03-20-10:00:28.960760UTC+0000_996ae14090d1">
  <Who>
    <Description>CHIME/FRB VOEvent Service</Description>
    <AuthorIVORN>ivo://ca.chimenet.frb/contact</AuthorIVORN>
    <Date>2022-03-20T10:00:28+00:00</Date>
    <Author>
      <contactEmail>andrew.zwaniga@mail.mcgill.ca</contactEmail>
      <contactName>Andrew Zwaniga</contactName>
      <shortName>CHIME/FRB VOEvent Service</shortName>
    </Author>
  </Who>
  <What>
    <Group name="observatory parameters">
      <Param ucd="time.resolution" unit="ms" value="0.983" name="sampling_time">
        <Description>FRB search time resolution</Description>
      </Param>
      <Param ucd="instr.bandwidth" unit="MHz" value="400" name="bandwidth">
        <Description>CHIME telescope bandwidth</Description>
      </Param>
      <Param ucd="em.freq;instr" unit="MHz" value="600" name="centre_frequency">
        <Description>CHIME telescope central frequency</Description>
      </Param>
      <Param ucd="" unit="" value="2" name="npol">
        <Description>The CHIME telescope has dual-polarization feeds</Description>
      </Param>
      <Param ucd="" unit="" value="8" name="bits_per_sample">
        <Description>CHIME/FRB samples 16384 frequency channels at 0.983 ms cadence as 8-bit integers</Description>
      </Param>
      <Param ucd="phot.antennaTemp" unit="K" value="50" name="tsys">
        <Description>CHIME receiver noise temperature</Description>
      </Param>
      <Param ucd="" unit="" value="" name="backend">
        <Description>CHIME/FRB backend</Description>
      </Param>
    </Group>
    <Group name="event parameters">
      <Param ucd="" unit="" value="217097677" name="event_no">
        <Description>CHIME/FRB event number assigned by real-time pipeline</Description>
      </Param>
      <Param ucd="" unit="" value="" name="known_source_name">
        <Description>CHIME/FRB internal known source name</Description>
      </Param>
      <Param ucd="" unit="" value="EXTRAGALACTIC" name="event_type">
        <Description>Unknown event type assigned from real-time pipeline e.g. EXTRAGALACTIC, AMBIGUOUS, GALACTIC</Description>
      </Param>
      <Param ucd="" unit="" value="real-time" name="pipeline_name">
        <Description>The name of the pipeline that produced this data</Description>
      </Param>
      <Param ucd="phys.dispMeasure" unit="pc/cm^3" value="308.1332092285156" name="dm">
        <Description>Dispersion measure from real-time pipeline</Description>
      </Param>
      <Param ucd="stat.error;phys.dispMeasure" unit="pc/cm^3" value="0.808748543262481" name="dm_error">
        <Description>Error in dispersion measure from real-time pipeline</Description>
      </Param>
      <Param ucd="" unit="" value="2022-03-20 10:00:28.960760+00:00" name="timestamp_utc">
        <Description>Topocentric arrival time at 400 MHz</Description>
      </Param>
      <Param ucd="" unit="" value="0.007864319719374001" name="timestamp_utc_error">
        <Description>Error in topocentric arrival time at 400 MHz in seconds from real-time pipeline</Description>
      </Param>
      <Param ucd="stat.snr" unit="" value="24.771873474121094" name="snr">
        <Description>Signal-to-noise ratio from real-time pipeline</Description>
      </Param>
      <Param ucd="" unit="degrees" value="0.5392466329194251" name="pos_error_semiminor_deg_95">
        <Description>Localization error ellipse semi-minor axis to 95 percent C.L. in right ascension (J2000) in degrees from real-time pipeline</Description>
      </Param>
      <Param ucd="" unit="degrees" value="0.38229381212162405" name="pos_error_semimajor_deg_95">
        <Description>Localization error ellipse semi-major axis to 95 percent C.L. in declination (J2000) in degrees from real-time pipeline</Description>
      </Param>
    </Group>
    <Group name="advanced parameters">
      <Param ucd="" unit="pc/cm^3" value="26.284419129901345" name="dm_gal_ne_2001_max">
        <Description>Max Milky Way DM contribution (NE 2001 model) from real-time pipeline</Description>
      </Param>
      <Param ucd="" unit="pc/cm^3" value="20.724408436144515" name="dm_gal_ymw_2016_max">
        <Description>Max Milky Way DM contribution (YMW 2016 model) from real-time pipeline</Description>
      </Param>
      <Param ucd="" unit="" value="2022-03-20 10:00:20.969754+00:00" name="timestamp_utc_inf_freq">
        <Description>Topocentric arrival time at infinite frequency</Description>
      </Param>
      <Param ucd="" unit="" value="0.02239969915578273" name="timestamp_utc_inf_freq_error">
        <Description>Error in topocentric arrival time at infinite frequency from real-time pipeline</Description>
      </Param>
    </Group>
  </What>
  <WhereWhen>
    <ObsDataLocation>
      <ObservatoryLocation id="CHIME lives at Dominion Radio Astrophysical Observatory (DRAO)"/>
      <ObservationLocation>
        <AstroCoordSystem id="UTC-FK5-TOPO"/>
        <AstroCoords coord_system_id="UTC-FK5-TOPO">
          <Time unit="s">
            <TimeInstant>
              <ISOTime>2022-03-20T10:00:28.960760</ISOTime>
            </TimeInstant>
          </Time>
          <Position2D unit="deg">
            <Name1>RA</Name1>
            <Name2>Dec</Name2>
            <Value2>
              <C1>207.13546129702095</C1>
              <C2>39.68328005638283</C2>
            </Value2>
            <Error2Radius>0.5392466329194251</Error2Radius>
          </Position2D>
        </AstroCoords>
      </ObservationLocation>
    </ObsDataLocation>
  </WhereWhen>
  <How>
    <Description>Real-time pipeline topocentric time-of-arrival is corrected for dispersion to bottom of CHIME band (400 MHz)</Description>
    <Reference uri="https://www.chime-frb.ca"/>
  </How>
  <Why importance="0.9999834084886757">
    <Inference probability="0" relation="">
      <Name/>
      <Concept>No probabilistic measurement is reported</Concept>
    </Inference>
    <Description>CHIME/FRB VOEvent Service detection-type alert from real-time pipeline</Description>
    <Name/>
    <Concept>Importance is a machine learning score from 0-1 separating RFI (0) from an astrophysical signal (1); Probability is not reported for the detection-type VOEvent</Concept>
  </Why>
</voe:VOEvent>"""
DUMMY_VOEVENT_CHIME = textwrap.dedent(DUMMY_VOEVENT_CHIME).strip().encode('UTF-8')


DUMMY_VOEVENT_GCN = u"""
<?xml version = "1.0" encoding = "UTF-8"?>
<voe:VOEvent
      ivorn="ivo://nasa.gsfc.gcn/SWIFT#BAT_QuickLook_Pos_1031728-518"
      role="observation" version="2.0"
      xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.ivoa.net/xml/VOEvent/v2.0  http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd" >
  <Who>
    <AuthorIVORN>ivo://nasa.gsfc.tan/gcn</AuthorIVORN>
    <Author>
      <shortName>VO-GCN</shortName>
      <contactName>Scott Barthelmy</contactName>
      <contactPhone>+1-301-286-3106</contactPhone>
      <contactEmail>scott.barthelmy@nasa.gov</contactEmail>
    </Author>
    <Date>2021-02-10T02:00:38</Date>
    <Description>This VOEvent message was created with GCN VOE version: 15.05 18nov20</Description>
  </Who>
  <What>
    <Param name="Packet_Type"   value="97" />
    <Param name="Pkt_Ser_Num"   value="1" />
    <Param name="TrigID"        value="1031728" ucd="meta.id" />
    <Param name="Segment_Num"   value="0" ucd="meta.id.part" />
    <Param name="Burst_TJD"     value="19255" unit="days" ucd="time" />
    <Param name="Burst_SOD"     value="7227.92" unit="sec" ucd="time" />
    <Param name="AT_Slew_Flags" value="0x3" />
    <Param name="Misc_flags"    value="0x0" />
    <Param name="Rate_Signif"   value="16.24" unit="sigma" ucd="stat.snr" />
    <Param name="SC_Long"       value="0.00" unit="deg" ucd="pos.earth.lon" />
    <Param name="SC_Lat"        value="0.00" unit="deg" ucd="pos.earth.lat" />
    <Group name="Misc_Flags" >
      <Param name="Values_Out_of_Range"      value="false" />
      <Param name="Near_Bright_Star"         value="false" />
      <Param name="Err_Circle_in_Galaxy"     value="false" />
      <Param name="Galaxy_in_Err_Circle"     value="false" />
      <Param name="TOO_Generated"            value="false" />
      <Param name="CRC_Error"                value="false" />
    </Group>
    <Param name="Coords_Type"   value="1" unit="dn" />
    <Param name="Coords_String" value="source_object" />
    <Group name="Obs_Support_Info" >
      <Description>The Sun and Moon values are valid at the time the VOEvent XML message was created.</Description>
      <Param name="Sun_RA"        value="323.93" unit="deg" ucd="pos.eq.ra" />
      <Param name="Sun_Dec"       value="-14.32" unit="deg" ucd="pos.eq.dec" />
      <Param name="Sun_Distance"  value="66.81" unit="deg" ucd="pos.angDistance" />
      <Param name="Sun_Hr_Angle"  value="4.06" unit="hr" />
      <Param name="Moon_RA"       value="303.40" unit="deg" ucd="pos.eq.ra" />
      <Param name="Moon_Dec"      value="-23.48" unit="deg" ucd="pos.eq.dec" />
      <Param name="MOON_Distance" value="54.85" unit="deg" ucd="pos.angDistance" />
      <Param name="Moon_Illum"    value="3.35" unit="%" ucd="arith.ratio" />
      <Param name="Galactic_Long" value="37.58" unit="deg" ucd="pos.galactic.lon" />
      <Param name="Galactic_Lat"  value="24.24" unit="deg" ucd="pos.galactic.lat" />
      <Param name="Ecliptic_Long" value="261.18" unit="deg" ucd="pos.ecliptic.lon" />
      <Param name="Ecliptic_Lat"  value="37.87" unit="deg" ucd="pos.ecliptic.lat" />
    </Group>
    <Description>Type=97: The Swift-BAT instrument quick-look position notice.</Description>
  </What>
  <WhereWhen>
    <ObsDataLocation>
      <ObservatoryLocation id="GEOLUN" />
      <ObservationLocation>
        <AstroCoordSystem id="UTC-FK5-GEO" />
        <AstroCoords coord_system_id="UTC-FK5-GEO">
          <Time unit="s">
            <TimeInstant>
              <ISOTime>2021-02-10T02:00:27.92</ISOTime>
            </TimeInstant>
          </Time>
          <Position2D unit="deg">
            <Name1>RA</Name1>
            <Name2>Dec</Name2>
            <Value2>
              <C1>262.8109</C1>
              <C2>14.6481</C2>
            </Value2>
            <Error2Radius>0.0500</Error2Radius>
          </Position2D>
        </AstroCoords>
      </ObservationLocation>
    </ObsDataLocation>
  <Description>The RA,Dec coordinates are of the type: source_object.</Description>
  </WhereWhen>
  <How>
    <Description>Swift Satellite, BAT Instrument</Description>
    <Reference uri="http://gcn.gsfc.nasa.gov/swift.html" type="url" />
  </How>
  <Why importance="0.90">
    <Inference probability="0.90">
      <Name>GRB 210210</Name>
      <Concept>process.variation.burst;em.gamma</Concept>
    </Inference>
  </Why>
  <Description>
  </Description>
</voe:VOEvent>
"""
DUMMY_VOEVENT_GCN = textwrap.dedent(DUMMY_VOEVENT_GCN).strip().encode('UTF-8')


DUMMY_VOEVENT_LIGO = u"""
<?xml version="1.0" encoding="UTF-8"?>
<voe:VOEvent xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0" xsi:schemaLocation="http://www.ivoa.net/xml/VOEvent/v2.0 http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd" version="2.0" role="test" ivorn="ivo://gwnet/LVC#MS220530p-2-Preliminary">
  <Who>
    <Date>2022-05-30T15:24:19</Date>
    <Author>
      <contactName>LIGO Scientific Collaboration and Virgo Collaboration</contactName>
    </Author>
  </Who>
  <What>
    <Param name="Packet_Type" value="150" dataType="int">
      <Description>The Notice Type number is assigned/used within GCN, eg type=150 is an LVC_PRELIMINARY notice</Description>
    </Param>
    <Param name="internal" value="0" dataType="int">
      <Description>Indicates whether this event should be distributed to LSC/Virgo members only</Description>
    </Param>
    <Param name="Pkt_Ser_Num" value="2" dataType="int">
      <Description>A number that increments by 1 each time a new revision is issued for this event</Description>
    </Param>
    <Param name="GraceID" value="MS220530p" ucd="meta.id" dataType="string">
      <Description>Identifier in GraceDB</Description>
    </Param>
    <Param name="AlertType" value="Preliminary" ucd="meta.version" dataType="string">
      <Description>VOEvent alert type</Description>
    </Param>
    <Param name="HardwareInj" value="0" ucd="meta.number" dataType="int">
      <Description>Indicates that this event is a hardware injection if 1, no if 0</Description>
    </Param>
    <Param name="OpenAlert" value="1" ucd="meta.number" dataType="int">
      <Description>Indicates that this event is an open alert if 1, no if 0</Description>
    </Param>
    <Param name="EventPage" value="https://gracedb.ligo.org/superevents/MS220530p/view/" ucd="meta.ref.url" dataType="string">
      <Description>Web page for evolving status of this GW candidate</Description>
    </Param>
    <Param name="Instruments" value="H1,L1" ucd="meta.code" dataType="string">
      <Description>List of instruments used in analysis to identify this event</Description>
    </Param>
    <Param name="FAR" value="9.110699364861297e-14" unit="Hz" ucd="arith.rate;stat.falsealarm" dataType="float">
      <Description>False alarm rate for GW candidates with this strength or greater</Description>
    </Param>
    <Param name="Group" value="CBC" ucd="meta.code" dataType="string">
      <Description>Data analysis working group</Description>
    </Param>
    <Param name="Pipeline" value="gstlal" ucd="meta.code" dataType="string">
      <Description>Low-latency data analysis pipeline</Description>
    </Param>
    <Param name="Search" value="MDC" ucd="meta.code" dataType="string">
      <Description>Specific low-latency search</Description>
    </Param>
    <Group name="GW_SKYMAP" type="GW_SKYMAP">
      <Param name="skymap_fits" value="https://gracedb.ligo.org/api/superevents/MS220530p/files/bayestar.fits.gz,1" ucd="meta.ref.url" dataType="string">
        <Description>Sky Map FITS</Description>
      </Param>
    </Group>
    <Group name="Classification" type="Classification">
      <Param name="BNS" value="0.9999981364395273" ucd="stat.probability" dataType="float">
        <Description>Probability that the source is a binary neutron star merger (both objects lighter than 3 solar masses)</Description>
      </Param>
      <Param name="NSBH" value="0.0" ucd="stat.probability" dataType="float">
        <Description>Probability that the source is a neutron star-black hole merger (primary heavier than 5 solar masses, secondary lighter than 3 solar masses)</Description>
      </Param>
      <Param name="BBH" value="0.0" ucd="stat.probability" dataType="float">
        <Description>Probability that the source is a binary black hole merger (both objects heavier than 5 solar masses)</Description>
      </Param>
      <Param name="MassGap" value="0.0" ucd="stat.probability" dataType="float">
        <Description>Probability that the source has at least one object between 3 and 5 solar masses</Description>
      </Param>
      <Param name="Terrestrial" value="1.863560472751012e-06" ucd="stat.probability" dataType="float">
        <Description>Probability that the source is terrestrial (i.e., a background noise fluctuation or a glitch)</Description>
      </Param>
      <Description>Source classification: binary neutron star (BNS), neutron star-black hole (NSBH), binary black hole (BBH), MassGap, or terrestrial (noise)</Description>
    </Group>
    <Group name="Properties" type="Properties">
      <Param name="HasNS" value="1.0" ucd="stat.probability" dataType="float">
        <Description>Probability that at least one object in the binary has a mass that is less than 3 solar masses</Description>
      </Param>
      <Param name="HasRemnant" value="1.0" ucd="stat.probability" dataType="float">
        <Description>Probability that a nonzero mass was ejected outside the central remnant object</Description>
      </Param>
      <Description>Qualitative properties of the source, conditioned on the assumption that the signal is an astrophysical compact binary merger</Description>
    </Group>
  </What>
  <WhereWhen>
    <ObsDataLocation>
      <ObservatoryLocation id="LIGO Virgo"/>
      <ObservationLocation>
        <AstroCoordSystem id="UTC-FK5-GEO"/>
        <AstroCoords coord_system_id="UTC-FK5-GEO">
          <Time unit="s">
            <TimeInstant>
              <ISOTime>2022-05-30T15:17:41</ISOTime>
            </TimeInstant>
          </Time>
        </AstroCoords>
      </ObservationLocation>
    </ObsDataLocation>
  </WhereWhen>
  <Description>Report of a candidate gravitational wave event</Description>
  <How>
    <Description>Candidate gravitational wave event identified by low-latency analysis</Description>
    <Description>H1: LIGO Hanford 4 km gravitational wave detector</Description>
    <Description>L1: LIGO Livingston 4 km gravitational wave detector</Description>
  </How>
  <Citations>
    <EventIVORN cite="supersedes">ivo://gwnet/LVC#MS220530p-1-Preliminary</EventIVORN>
    <Description>Initial localization is now available (preliminary)</Description>
  </Citations>
</voe:VOEvent>
"""
DUMMY_VOEVENT_LIGO = textwrap.dedent(DUMMY_VOEVENT_LIGO).strip().encode('UTF-8')

DUMMY_VOEVENT_LIGO_PRELIMINARY = u"""
<?xml version="1.0" encoding="UTF-8"?>
<voe:VOEvent xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0" xsi:schemaLocation="http://www.ivoa.net/xml/VOEvent/v2.0 http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd" version="2.0" role="test" ivorn="ivo://gwnet/LVC#MS220706b-1-Preliminary">
  <Who>
    <Date>2022-07-06T01:38:52</Date>
    <Author>
      <contactName>LIGO Scientific Collaboration and Virgo Collaboration</contactName>
    </Author>
  </Who>
  <What>
    <Param name="Packet_Type" value="150" dataType="int">
      <Description>The Notice Type number is assigned/used within GCN, eg type=150 is an LVC_PRELIMINARY notice</Description>
    </Param>
    <Param name="internal" value="0" dataType="int">
      <Description>Indicates whether this event should be distributed to LSC/Virgo members only</Description>
    </Param>
    <Param name="Pkt_Ser_Num" value="1" dataType="int">
      <Description>A number that increments by 1 each time a new revision is issued for this event</Description>
    </Param>
    <Param name="GraceID" value="MS220706b" ucd="meta.id" dataType="string">
      <Description>Identifier in GraceDB</Description>
    </Param>
    <Param name="AlertType" value="Preliminary" ucd="meta.version" dataType="string">
      <Description>VOEvent alert type</Description>
    </Param>
    <Param name="HardwareInj" value="0" ucd="meta.number" dataType="int">
      <Description>Indicates that this event is a hardware injection if 1, no if 0</Description>
    </Param>
    <Param name="OpenAlert" value="1" ucd="meta.number" dataType="int">
      <Description>Indicates that this event is an open alert if 1, no if 0</Description>
    </Param>
    <Param name="EventPage" value="https://gracedb.ligo.org/superevents/MS220706b/view/" ucd="meta.ref.url" dataType="string">
      <Description>Web page for evolving status of this GW candidate</Description>
    </Param>
    <Param name="Instruments" value="H1,L1" ucd="meta.code" dataType="string">
      <Description>List of instruments used in analysis to identify this event</Description>
    </Param>
    <Param name="FAR" value="9.110699364861297e-14" unit="Hz" ucd="arith.rate;stat.falsealarm" dataType="float">
      <Description>False alarm rate for GW candidates with this strength or greater</Description>
    </Param>
    <Param name="Group" value="CBC" ucd="meta.code" dataType="string">
      <Description>Data analysis working group</Description>
    </Param>
    <Param name="Pipeline" value="gstlal" ucd="meta.code" dataType="string">
      <Description>Low-latency data analysis pipeline</Description>
    </Param>
    <Param name="Search" value="MDC" ucd="meta.code" dataType="string">
      <Description>Specific low-latency search</Description>
    </Param>
    <Group name="GW_SKYMAP" type="GW_SKYMAP">
      <Param name="skymap_fits" value="https://gracedb.ligo.org/api/superevents/MS220706b/files/bayestar.fits.gz,0" ucd="meta.ref.url" dataType="string">
        <Description>Sky Map FITS</Description>
      </Param>
    </Group>
    <Group name="Classification" type="Classification">
      <Param name="BNS" value="0.9999773696256827" ucd="stat.probability" dataType="float">
        <Description>Probability that the source is a binary neutron star merger (both objects lighter than 3 solar masses)</Description>
      </Param>
      <Param name="NSBH" value="0.0" ucd="stat.probability" dataType="float">
        <Description>Probability that the source is a neutron star-black hole merger (primary heavier than 5 solar masses, secondary lighter than 3 solar masses)</Description>
      </Param>
      <Param name="BBH" value="0.0" ucd="stat.probability" dataType="float">
        <Description>Probability that the source is a binary black hole merger (both objects heavier than 5 solar masses)</Description>
      </Param>
      <Param name="Terrestrial" value="2.2630374317225275e-05" ucd="stat.probability" dataType="float">
        <Description>Probability that the source is terrestrial (i.e., a background noise fluctuation or a glitch)</Description>
      </Param>
      <Description>Source classification: binary neutron star (BNS), neutron star-black hole (NSBH), binary black hole (BBH), MassGap, or terrestrial (noise)</Description>
    </Group>
    <Group name="Properties" type="Properties">
      <Param name="HasNS" value="1.0" ucd="stat.probability" dataType="float">
        <Description>Probability that at least one object in the binary has a mass that is less than 3 solar masses</Description>
      </Param>
      <Param name="HasRemnant" value="1.0" ucd="stat.probability" dataType="float">
        <Description>Probability that a nonzero mass was ejected outside the central remnant object</Description>
      </Param>
      <Description>Qualitative properties of the source, conditioned on the assumption that the signal is an astrophysical compact binary merger</Description>
    </Group>
  </What>
  <WhereWhen>
    <ObsDataLocation>
      <ObservatoryLocation id="LIGO Virgo"/>
      <ObservationLocation>
        <AstroCoordSystem id="UTC-FK5-GEO"/>
        <AstroCoords coord_system_id="UTC-FK5-GEO">
          <Time unit="s">
            <TimeInstant>
              <ISOTime>2022-07-06T01:37:25</ISOTime>
            </TimeInstant>
          </Time>
        </AstroCoords>
      </ObservationLocation>
    </ObsDataLocation>
  </WhereWhen>
  <Description>Report of a candidate gravitational wave event</Description>
  <How>
    <Description>Candidate gravitational wave event identified by low-latency analysis</Description>
    <Description>H1: LIGO Hanford 4 km gravitational wave detector</Description>
    <Description>L1: LIGO Livingston 4 km gravitational wave detector</Description>
  </How>
</voe:VOEvent>
"""
DUMMY_VOEVENT_LIGO_PRELIMINARY = textwrap.dedent(DUMMY_VOEVENT_LIGO_PRELIMINARY).strip().encode('UTF-8')

DUMMY_VOEVENT_INTEGRAL_GCN = u"""
"""
DUMMY_VOEVENT_INTEGRAL_GCN = textwrap.dedent(DUMMY_VOEVENT_INTEGRAL_GCN).strip().encode('UTF-8')

DUMMY_VOEVENT_LIGO_INITIAL = u"""
<?xml version="1.0" encoding="UTF-8"?>
<voe:VOEvent xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0" xsi:schemaLocation="http://www.ivoa.net/xml/VOEvent/v2.0 http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd" version="2.0" role="test" ivorn="ivo://gwnet/LVC#MS220706b-3-Initial">
  <Who>
    <Date>2022-07-06T01:48:55</Date>
    <Author>
      <contactName>LIGO Scientific Collaboration and Virgo Collaboration</contactName>
    </Author>
  </Who>
  <What>
    <Param name="Packet_Type" value="151" dataType="int">
      <Description>The Notice Type number is assigned/used within GCN, eg type=151 is an LVC_INITIAL notice</Description>
    </Param>
    <Param name="internal" value="0" dataType="int">
      <Description>Indicates whether this event should be distributed to LSC/Virgo members only</Description>
    </Param>
    <Param name="Pkt_Ser_Num" value="3" dataType="int">
      <Description>A number that increments by 1 each time a new revision is issued for this event</Description>
    </Param>
    <Param name="GraceID" value="MS220706b" ucd="meta.id" dataType="string">
      <Description>Identifier in GraceDB</Description>
    </Param>
    <Param name="AlertType" value="Initial" ucd="meta.version" dataType="string">
      <Description>VOEvent alert type</Description>
    </Param>
    <Param name="HardwareInj" value="0" ucd="meta.number" dataType="int">
      <Description>Indicates that this event is a hardware injection if 1, no if 0</Description>
    </Param>
    <Param name="OpenAlert" value="1" ucd="meta.number" dataType="int">
      <Description>Indicates that this event is an open alert if 1, no if 0</Description>
    </Param>
    <Param name="EventPage" value="https://gracedb.ligo.org/superevents/MS220706b/view/" ucd="meta.ref.url" dataType="string">
      <Description>Web page for evolving status of this GW candidate</Description>
    </Param>
    <Param name="Instruments" value="H1,L1" ucd="meta.code" dataType="string">
      <Description>List of instruments used in analysis to identify this event</Description>
    </Param>
    <Param name="FAR" value="9.110699364861297e-14" unit="Hz" ucd="arith.rate;stat.falsealarm" dataType="float">
      <Description>False alarm rate for GW candidates with this strength or greater</Description>
    </Param>
    <Param name="Group" value="CBC" ucd="meta.code" dataType="string">
      <Description>Data analysis working group</Description>
    </Param>
    <Param name="Pipeline" value="gstlal" ucd="meta.code" dataType="string">
      <Description>Low-latency data analysis pipeline</Description>
    </Param>
    <Param name="Search" value="MDC" ucd="meta.code" dataType="string">
      <Description>Specific low-latency search</Description>
    </Param>
    <Group name="GW_SKYMAP" type="GW_SKYMAP">
      <Param name="skymap_fits" value="https://gracedb.ligo.org/api/superevents/MS220706b/files/bayestar.fits.gz,1" ucd="meta.ref.url" dataType="string">
        <Description>Sky Map FITS</Description>
      </Param>
    </Group>
    <Group name="Classification" type="Classification">
      <Param name="BNS" value="0.9999773696256827" ucd="stat.probability" dataType="float">
        <Description>Probability that the source is a binary neutron star merger (both objects lighter than 3 solar masses)</Description>
      </Param>
      <Param name="NSBH" value="0.0" ucd="stat.probability" dataType="float">
        <Description>Probability that the source is a neutron star-black hole merger (primary heavier than 5 solar masses, secondary lighter than 3 solar masses)</Description>
      </Param>
      <Param name="BBH" value="0.0" ucd="stat.probability" dataType="float">
        <Description>Probability that the source is a binary black hole merger (both objects heavier than 5 solar masses)</Description>
      </Param>
      <Param name="Terrestrial" value="2.2630374317225275e-05" ucd="stat.probability" dataType="float">
        <Description>Probability that the source is terrestrial (i.e., a background noise fluctuation or a glitch)</Description>
      </Param>
      <Description>Source classification: binary neutron star (BNS), neutron star-black hole (NSBH), binary black hole (BBH), MassGap, or terrestrial (noise)</Description>
    </Group>
    <Group name="Properties" type="Properties">
      <Param name="HasNS" value="1.0" ucd="stat.probability" dataType="float">
        <Description>Probability that at least one object in the binary has a mass that is less than 3 solar masses</Description>
      </Param>
      <Param name="HasRemnant" value="1.0" ucd="stat.probability" dataType="float">
        <Description>Probability that a nonzero mass was ejected outside the central remnant object</Description>
      </Param>
      <Description>Qualitative properties of the source, conditioned on the assumption that the signal is an astrophysical compact binary merger</Description>
    </Group>
  </What>
  <WhereWhen>
    <ObsDataLocation>
      <ObservatoryLocation id="LIGO Virgo"/>
      <ObservationLocation>
        <AstroCoordSystem id="UTC-FK5-GEO"/>
        <AstroCoords coord_system_id="UTC-FK5-GEO">
          <Time unit="s">
            <TimeInstant>
              <ISOTime>2022-07-06T01:37:25</ISOTime>
            </TimeInstant>
          </Time>
        </AstroCoords>
      </ObservationLocation>
    </ObsDataLocation>
  </WhereWhen>
  <Description>Report of a candidate gravitational wave event</Description>
  <How>
    <Description>Candidate gravitational wave event identified by low-latency analysis</Description>
    <Description>H1: LIGO Hanford 4 km gravitational wave detector</Description>
    <Description>L1: LIGO Livingston 4 km gravitational wave detector</Description>
  </How>
  <Citations>
    <EventIVORN cite="supersedes">ivo://gwnet/LVC#MS220706b-2-Preliminary</EventIVORN>
    <EventIVORN cite="supersedes">ivo://gwnet/LVC#MS220706b-1-Preliminary</EventIVORN>
    <Description>Initial localization is now available</Description>
  </Citations>
</voe:VOEvent>
"""
DUMMY_VOEVENT_LIGO_INITIAL = textwrap.dedent(DUMMY_VOEVENT_LIGO_INITIAL).strip().encode('UTF-8')

DUMMY_VOEVENT_GCN_FERMI = u"""
<?xml version = "1.0" encoding = "UTF-8"?>
<voe:VOEvent
      ivorn="ivo://nasa.gsfc.gcn/Fermi#LAT_Monitor_2022-07-10T12:00:00.00_1657551149-0-601"
      role="observation" version="2.0"
      xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.ivoa.net/xml/VOEvent/v2.0  http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd" >
  <Who>
    <AuthorIVORN>ivo://nasa.gsfc.tan/gcn</AuthorIVORN>
    <Author>
      <shortName>Fermi (via VO-GCN)</shortName>
      <contactName>David Thompson</contactName>
      <contactPhone>+1-301-286-8168</contactPhone>
      <contactEmail>David.J.Thompson@nasa.gov</contactEmail>
    </Author>
    <Date>2022-07-11T14:52:29</Date>
    <Description>This VOEvent message was created with GCN VOE version: 15.08 17jun22</Description>
  </Who>
  <What>
    <Param name="Packet_Type"   value="125" />
    <Param name="Pkt_Ser_Num"   value="2" />
    <Param name="SourceName"    value="PMNJ2141-6411_86400.png" ucd="meta.id" />
    <Param name="TrigID"        value="1657551149" ucd="meta.id" />
    <Param name="Record_Num"    value="0" ucd="meta.id.part" />
    <Param name="Trans_TJD"     value="19770" unit="days" ucd="time" />
    <Param name="Trans_SOD"     value="43200.00" unit="sec" ucd="time" />
    <Param name="Curr_Flux"     value="4.700e-07" unit="cts" ucd="phot.count" />
    <Param name="Base_Flux"     value="1.500e-07" unit="cts" ucd="phot.count" />
    <Param name="Curr_Flux_Err" value="2.800e-08" unit="cts" ucd="phot.count" />
    <Param name="Base_Flux_Err" value="4.500e-08" unit="cts" ucd="phot.count" />
    <Param name="Time_Scale"    value="0" unit="dn" ucd="time.interval" />
    <Param name="E_Band_Lo"     value="300.0" />
    <Param name="E_Band_Hi"     value="0.1" />
    <Param name="Signif"        value="60900.00" />
    <Param name="Trigger_ID"    value="0x0" />
    <Param name="Misc_flags"    value="0x40000000" />
    <Group name="Trigger_ID" >
      <Param name="Retraction"             value="false" />
      <Param name="Spatial_Prox_Match"     value="false" />
      <Param name="Temporal_Prox_Match"    value="false" />
    </Group>
    <Group name="Misc_Flags" >
      <Param name="Values_Out_of_Range"    value="false" />
      <Param name="Near_Bright_Star"       value="false" />
      <Param name="Err_Circle_in_Galaxy"   value="false" />
      <Param name="Galaxy_in_Err_Circle"   value="false" />
    </Group>
    <Param name="Coords_Type"   value="1" unit="dn" />
    <Param name="Coords_String" value="source_object" />
    <Param name="LC_URL" value="http://fermi.gsfc.nasa.gov/FTP/glast/data/lat/catalogs/asp/current/lightcurves/PMNJ2141-6411_86400.png" ucd="meta.ref.url" />
    <Group name="Obs_Support_Info" >
      <Description>The Sun and Moon values are valid at the time the VOEvent XML message was created.</Description>
      <Param name="Sun_RA"        value="110.89" unit="deg" ucd="pos.eq.ra" />
      <Param name="Sun_Dec"       value="22.05" unit="deg" ucd="pos.eq.dec" />
      <Param name="Sun_Distance"  value="132.03" unit="deg" ucd="pos.angDistance" />
      <Param name="Sun_Hr_Angle"  value="9.67" unit="hr" />
      <Param name="Moon_RA"       value="257.46" unit="deg" ucd="pos.eq.ra" />
      <Param name="Moon_Dec"      value="-25.41" unit="deg" ucd="pos.eq.dec" />
      <Param name="MOON_Distance" value="57.91" unit="deg" ucd="pos.angDistance" />
      <Param name="Moon_Illum"    value="93.10" unit="%" ucd="arith.ratio" />
      <Param name="Galactic_Long" value="328.61" unit="deg" ucd="pos.galactic.lon" />
      <Param name="Galactic_Lat"  value="-42.28" unit="deg" ucd="pos.galactic.lat" />
      <Param name="Ecliptic_Long" value="301.52" unit="deg" ucd="pos.ecliptic.lon" />
      <Param name="Ecliptic_Lat"  value="-46.69" unit="deg" ucd="pos.ecliptic.lat" />
    </Group>
    <Description>The Fermi-LAT detection of a flare from a known source.</Description>
  </What>
  <WhereWhen>
    <ObsDataLocation>
      <ObservatoryLocation id="GEOLUN" />
      <ObservationLocation>
        <AstroCoordSystem id="UTC-FK5-GEO" />
        <AstroCoords coord_system_id="UTC-FK5-GEO">
          <Time unit="s">
            <TimeInstant>
              <ISOTime>2022-07-10T12:00:00.00</ISOTime>
            </TimeInstant>
          </Time>
          <Position2D unit="deg">
            <Name1>RA</Name1>
            <Name2>Dec</Name2>
            <Value2>
              <C1>325.4429</C1>
              <C2>-64.1869</C2>
            </Value2>
            <Error2Radius>0.0000</Error2Radius>
          </Position2D>
        </AstroCoords>
      </ObservationLocation>
    </ObsDataLocation>
  <Description>The RA,Dec coordinates are of the type: source_object.</Description>
  </WhereWhen>
  <How>
    <Description>Fermi Satellite, LAT Instrument</Description>
    <Reference uri="http://gcn.gsfc.nasa.gov/fermi.html" type="url" />
  </How>
  <Why importance="0.5">
    <Inference probability="0.9">
      <Concept>process.variation.burst;em.gamma</Concept>
    </Inference>
  </Why>
  <Description>
  </Description>
</voe:VOEvent>
"""
DUMMY_VOEVENT_GCN_FERMI = textwrap.dedent(DUMMY_VOEVENT_GCN_FERMI).strip().encode('UTF-8')