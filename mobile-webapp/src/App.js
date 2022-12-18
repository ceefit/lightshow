import React, {useCallback, useEffect, useState} from 'react';
import {Box, Button, Card, Carousel, dark, Grommet, Heading, Page, PageContent, PageHeader, Paragraph, Text} from 'grommet';
import axios from 'axios';

dark.global.font.family = "Roboto"

function App() {

  const [showStatus, setShowStatus] = useState("loading")
  const [timeRemaining, setTimeRemaining] = useState("0:00")
  const [error, setError] = useState(false)
  const [activeSlide, setActiveSlide] = React.useState(0);

  const sendHit = useCallback(() => {
    axios.get(`${process.env.REACT_APP_API_HOST}/hit`)
      .then(setError(false))
      .catch(e => {
        setError(true)
      })
  }, [setError])

  const checkStatus = useCallback(() => {
    axios.get(`${process.env.REACT_APP_API_HOST}/status`)
      .then(res => {
          if (200 >= res.status <= 299) {
            setError(false)
            setShowStatus(res.data.status)
            setTimeRemaining(res.data.time_remaining)
          }
        }
      )
      .catch(e => {
        setError(true)
      })
  }, [setError, setShowStatus, setShowStatus, setTimeRemaining])

  const startShow = useCallback(() => {
    axios.get(`${process.env.REACT_APP_API_HOST}/start_show`)
      .then(setError(false))
      .catch(e => {
        setError(true)
      })
  }, [setError])


  useEffect(() => {
    sendHit()
  }, [sendHit])

  useEffect(() => {
    setInterval(checkStatus, 1000)
  }, [checkStatus])

  const contentBody = () => {
    if (error) {
      return (
        <Paragraph>
          Error contacting lights show. Try refreshing the page
        </Paragraph>
      )
    } else {
      if (showStatus === "off") {
        return (
          <>
            <iframe width="300" height="225" src="https://www.youtube.com/embed/gz3W89PWipQ"
                    title="2022 Noor Lane Lights Show - Trans-Siberian Orchestra - Christmas Eve/Sarajevo - Carol of the Bells"
                    frameBorder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen=""></iframe>
            <Heading>
              Next show starts in {timeRemaining}
            </Heading>
          </>
        )
      }

      if (showStatus === "busy") {
        return (
          <>
            <Text weight="bold" size="xlarge">
            Trans-Siberian Orchestra - Christmas Eve/Sarajevo - Carol of the Bells
            </Text>
            <Text weight="bold" size="xlarge">
            {timeRemaining}
            </Text>
          </>
        )
      }

      if (showStatus === "loading") {
        return (
          <>
            <Paragraph>
              Preparing Lights Show...
            </Paragraph>
          </>
        )
      }

      if (showStatus === "ready") {
        return (
          <Box align="center" background={"dark-1"}>
            <Carousel controls={false} activeChild={activeSlide} onChild={setActiveSlide} height="small" width="large">
              <Box
                align="center"
                justify="center"
                gap="small"
              >
                <Card margin={"small"}>
                  <Box>
                    <Text weight="bold" size="xlarge">
                      Wait until you hear the greeting on your car radio, then tap the button
                    </Text>
                    <Button label="I hear it!" onClick={() => setActiveSlide(activeSlide + 1)}/>
                  </Box>
                </Card>
              </Box>
              <Box
                align="center"
                justify="center"
                gap="small"
              >
                <Card margin={"small"}>
                  <Text weight="bold" size="xlarge">
                    When you're ready to begin the show, tap the button
                  </Text>
                  <Button label="Start the show" onClick={() => {
                    startShow()
                  }}/>
                </Card>
              </Box>
            </Carousel>
          </Box>
        )
      }
    }
  }


  const header = () => {
    if (showStatus === "off") {
      return (
        <Heading>
          Showtime is 5-10pm. Check back soon!
        </Heading>
      )
    } else {
      return (
        <Heading>
          Tune your radio to 104.5 FM
        </Heading>
      )
    }
  }

  return (
    <Grommet theme={dark} themeMode={'dark'} full={true}>
      <Page kind={"wide"} align={'center'}>
        <PageHeader
          title={"2022 Noor Lane Lights Show"}
          size={"large"}
        />
        <PageContent align={'center'}>
          {header()}

          {contentBody()}

          <Box height={"2000px"}/>
          <Paragraph fill={true}>
            This site doesn't use cookies (we saved them for santa)
          </Paragraph>
        </PageContent>
      </Page>
    </Grommet>
  );
}

export default App;
