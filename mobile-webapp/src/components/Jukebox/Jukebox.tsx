import Paper from '@mui/material/Paper'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import {ThemeProvider} from './theme'

import './Jukebox.css'
import {
  Avatar,
  Button, Divider,
  List,
  ListItem,
  ListItemAvatar, ListItemText
} from "@mui/material";
import mariahCareyIcon from '../../img/Mariah_Carey.png'
import lindsaySterlingIcon from '../../img/Lindsay_Sterling.png'
import transSiberianOrchestraIcon from '../../img/Trans_Siberian_Orchestra.png'

const Jukebox = () => {

    const tracks = [
        {"artist": "Mariah Carey", "song": "All I Want For Christmas Is You", "albumArt": mariahCareyIcon},
        {"artist": "Lindsay Sterling", "song": "Carol Of The Bells", "albumArt": lindsaySterlingIcon},
        {"artist": "Trans-Siberian Orchestra", "song": "Christmas Sarajevo", "albumArt": transSiberianOrchestraIcon},
    ]

    const renderTrackList = () => {
        const renderListItem = (track: { artist: string, song: string, albumArt: string }) => {
            return (
                <Button sx={{width: "100%"}} variant="text">
                    <ListItem  key={track.song} >
                        <ListItemAvatar>
                            <Avatar variant="rounded" sx={{ width: '10vw', height: '10vw', margin:'16px'}}>
                                <img alt={track.artist} width="100%" height="100%" src={track.albumArt}/>
                            </Avatar>
                        </ListItemAvatar>
                        <ListItemText primary={track.song} secondary={track.artist} sx={{ width: '100%'}}/>
                    </ListItem>
                </Button>
            )
        }

        const result = []
        for (const trackIdx in tracks) {
            result.push(renderListItem(tracks[trackIdx]))
            result.push(<Divider variant="inset" component="li" />)
        }
        result.pop()

        return <List sx={{bgcolor: 'background.paper'}}>
            {result}
        </List>
    }

    return (
        <ThemeProvider>
            <Paper className="jukebox-container" sx={{maxWidth: "600px"}}>
                <Stack spacing={1}>
                    <Typography align="center" variant="h5">
                        2023 Noor Lane Lights Show
                    </Typography>
                    <Typography align="center" variant="h4">
                        104.5FM
                    </Typography>
                  {renderTrackList()}
                </Stack>
            </Paper>
        </ThemeProvider>
    )
}

export default Jukebox
