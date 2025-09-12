"""
AniList API service for fetching manga metadata.
"""

import requests
from typing import Dict, Optional, Any
import logging

from ..config.settings import ANILIST_URL, REQUEST_TIMEOUT


logger = logging.getLogger(__name__)


class AniListService:
    """Service for interacting with the AniList GraphQL API."""
    
    MANGA_QUERY = '''
    query ($search: String) {
        Media(search: $search, type: MANGA) {
            id
            title {
                romaji
                english
                native
            }
            coverImage {
                extraLarge
                large
                medium
            }
            description(asHtml: false)
            siteUrl
            status
            format
            startDate {
                year
                month
                day
            }
            endDate {
                year
                month
                day
            }
            chapters
            volumes
            genres
            tags {
                name
                description
            }
            averageScore
            popularity
            staff {
                edges {
                    node {
                        name {
                            full
                        }
                    }
                    role
                }
            }
        }
    }
    '''
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
    
    def search_manga(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Search for manga metadata on AniList.
        
        Args:
            title: Manga title to search for
            
        Returns:
            Manga metadata dictionary or None if not found
        """
        if not title.strip():
            return None
        
        variables = {'search': title.strip()}
        payload = {
            'query': self.MANGA_QUERY,
            'variables': variables
        }
        
        try:
            logger.debug(f"Searching AniList for: {title}")
            response = self.session.post(
                ANILIST_URL,
                json=payload,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                media = data.get('data', {}).get('Media')
                
                if media:
                    logger.info(f"Found metadata for: {title}")
                    return self._process_media_data(media)
                else:
                    logger.warning(f"No metadata found for: {title}")
                    return None
            else:
                # Log as warning instead of error to avoid notifications
                logger.warning(f"AniList API returned status {response.status_code}")
                return None
                
        except requests.RequestException as e:
            # Log as warning instead of error to avoid notifications
            logger.warning(f"Request failed for {title}: {e}")
            return None
        except Exception as e:
            # Log as warning instead of error to avoid notifications
            logger.warning(f"Unexpected error searching for {title}: {e}")
            return None
    
    def _process_media_data(self, media: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and clean the media data from AniList.
        
        Args:
            media: Raw media data from AniList
            
        Returns:
            Processed media data
        """
        # Extract staff information
        authors = []
        artists = []
        
        if 'staff' in media and 'edges' in media['staff']:
            for edge in media['staff']['edges']:
                role = edge.get('role', '').lower()
                name = edge.get('node', {}).get('name', {}).get('full')
                
                if name:
                    if 'story' in role or 'original' in role:
                        authors.append(name)
                    elif 'art' in role:
                        artists.append(name)
        
        # Process dates
        start_date = self._format_date(media.get('startDate'))
        end_date = self._format_date(media.get('endDate'))
        
        return {
            'id': media.get('id'),
            'title': media.get('title', {}),
            'coverImage': media.get('coverImage', {}),
            'description': media.get('description'),
            'siteUrl': media.get('siteUrl'),
            'status': media.get('status'),
            'format': media.get('format'),
            'startDate': start_date,
            'endDate': end_date,
            'chapters': media.get('chapters'),
            'volumes': media.get('volumes'),
            'genres': media.get('genres', []),
            'tags': [tag.get('name') for tag in media.get('tags', []) if tag.get('name')],
            'averageScore': media.get('averageScore'),
            'popularity': media.get('popularity'),
            'authors': authors,
            'artists': artists,
        }
    
    def _format_date(self, date_obj: Optional[Dict[str, int]]) -> Optional[str]:
        """
        Format a date object from AniList to a string.
        
        Args:
            date_obj: Date object with year, month, day keys
            
        Returns:
            Formatted date string or None
        """
        if not date_obj or not date_obj.get('year'):
            return None
        
        year = date_obj['year']
        month = date_obj.get('month', 1)
        day = date_obj.get('day', 1)
        
        return f"{year:04d}-{month:02d}-{day:02d}"
    
    def download_image(self, url: str) -> Optional[bytes]:
        """
        Download an image from a URL.
        
        Args:
            url: Image URL
            
        Returns:
            Image data as bytes or None if failed
        """
        if not url:
            return None
        
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                return response.content
            else:
                logger.warning(f"Failed to download image: {url} (status: {response.status_code})")
                return None
        except requests.RequestException as e:
            # Log as warning instead of error to avoid notifications
            logger.warning(f"Error downloading image {url}: {e}")
            return None