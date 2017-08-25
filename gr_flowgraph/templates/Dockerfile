#{#
# This file is protected by Copyright. Please refer to the COPYRIGHT file
# distributed with this source distribution.
#
# This file is part of GNURadio REDHAWK.
#
# GNURadio REDHAWK is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# GNURadio REDHAWK is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#}
#% set componentdir = component.name.replace('.','/')
FROM geontech/gnuradio-redhawk-runtime:{{ versions.codegen }}
LABEL name="REDHAWK+GNURadio {{ component.name }} Runtime Container"

ADD . /root/{{ component.name }}
RUN printf '\
. /etc/profile\n\
mv /root/{{ component.name }} $SDRROOT/{{component.sdrpath}}/{{componentdir}}\n\
chown -R redhawk:redhawk $SDRROOT\n\
chmod -R g+ws $SDRROOT\n\
' | bash && \
    #
    # Tweak the entry point to source /etc/profile first
    #
    printf '#!/usr/bin/env bash \n\
. /etc/profile \n\
exec $@\n\
' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]
WORKDIR {{component.env_sdrroot}}
