package second_in_command.skills.strikecraft

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class Huntsman : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "所有战机"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("+25%% 对护卫舰的伤害", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

        tooltip.addSpacer(10f)
        tooltip.addPara("影响：{地面行动", 0f, Misc.getGrayColor(), Misc.getBasePlayerColor(), "地面行动")
        tooltip.addSpacer(10f)

        tooltip.addPara("+20%% 突袭等地面作战行动的效果", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {

    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {

    }

    override fun applyEffectsToFighterSpawnedByShip(data: SCData, fighter: ShipAPI?, ship: ShipAPI?, id: String?) {
        var stats = fighter!!.mutableStats

        stats.damageToFrigates.modifyPercent(id, 25f)
    }

    override fun advance(data: SCData, amunt: Float?) {
        data.fleet.stats.dynamic.getMod(Stats.PLANETARY_OPERATIONS_MOD).modifyPercent("sc_huntsman", 20f, "迅捷猎手")
    }

    override fun onActivation(data: SCData) {
        data.fleet.stats.dynamic.getMod(Stats.PLANETARY_OPERATIONS_MOD).modifyPercent("sc_huntsman", 20f, "迅捷猎手")
    }

    override fun onDeactivation(data: SCData) {
        data.fleet.stats.dynamic.getMod(Stats.PLANETARY_OPERATIONS_MOD).unmodify("sc_huntsman")
    }
}