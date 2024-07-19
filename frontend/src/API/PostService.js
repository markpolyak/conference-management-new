import axios from "axios";

const CONFERENCES_URL = '/data/conferences.json';
const CONFERENCE_URL = '/data/conference.json';

class PostService {
    static async getConferences(filter) {
        const response = await axios.get(CONFERENCES_URL, {
            params: {
                filter: filter
            }
        });
        return response.data;
    }

    static async getConference(conference_id, token = '') {

        const config = token ? {
            params: {
                conference_id
            },
            headers: {
                Authorization: `Bearer ${token}`
            }
        }
        : 
        {
            params: {
                conference_id
            },
        }

        const response = await axios.get(CONFERENCE_URL, config)

        return response.data;
    }

    static async getApplications(conference_id, params = {telegram_id:"", discord_id:"", email:""}) {
        const response = await axios.get('/data/applications.json', {
            params: {
                conference_id,
                ...params
            }
        })

        return response.data;
    }

    static async postApplication(conference_id, application) {
        const response = await axios.post(`/conferences/${conference_id}/applications`, application);

        return response.data;
    }

    static async patchApplication(conference_id, application) {
        const response = await axios.patch(`/conferences/${conference_id}/applications/${application.id}`, application);

        return response.data;
    }

    static async deleteApplication(conference_id, application) {
        const response = await axios.delete(`/conferences/${conference_id}/applications/${application.id}`, application);

        return response.data;
    }
}

export default PostService;