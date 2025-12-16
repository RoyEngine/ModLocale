package second_in_command.skills.smallcraft

import com.fs.starfarer.api.GameState
import com.fs.starfarer.api.Global
import com.fs.starfarer.api.campaign.CampaignFleetAPI
import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.misc.levelBetween
import second_in_command.specs.SCBaseSkillPlugin

class LowProfile : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "all ships in the fleet"
    }

    fun getFleetDP(fleet: CampaignFleetAPI) : Float {
        if (Global.getCurrentState() == GameState.TITLE) return 0f
        var DP = 0f
        for (member in fleet.fleetData.membersListCopy) {
            if (!member.isFrigate && !member.isDestroyer) continue
            DP += member.deploymentPointsCost
        }
        return DP
    }

    fun getBonus(fleet: CampaignFleetAPI) : Float {
       return 0.25f * getFleetDP(fleet).levelBetween(0f, 240f)
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        var DP = getFleetDP(data.fleet).toInt()
        var bonus = (getBonus(data.fleet) * 100).toInt()

        tooltip.addPara("+1 当舰队处于 缓速航行* 时的最大宇宙航行速度", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("根据舰队中护卫舰和驱逐舰的数量，减少舰队的被侦测范围", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("   - 根据舰队中护卫舰和驱逐舰的部署点数，减少幅度位于 0%%-25%% 之间",0f, Misc.getTextColor(), Misc.getHighlightColor(), "0%","25%")
        tooltip.addPara("   - 护卫舰和驱逐舰总计达到 240 部署点数}时效果达到最大值",0f, Misc.getTextColor(), Misc.getHighlightColor(), "240 部署点数")
        tooltip.addPara("   - 舰队当前总部署点数为 $DP}，减少幅度为 $bonus%%",0f, Misc.getTextColor(), Misc.getHighlightColor(), "$DP", "$bonus%")

        tooltip.addSpacer(10f)

        tooltip.addPara("*缓速航行的舰队在某些地形中更难被发现，并且可以避免某些危险。有些能力能够减慢" +
                "舰队的航行速度。当舰队的移动速度为舰队中最慢舰船的最大宇宙航速的一半时，该舰队视作 缓速航行。", 0f, Misc.getGrayColor(), Misc.getHighlightColor())
    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {

    }

    override fun advance(data: SCData, amount: Float) {
        data.fleet.stats.dynamic.getMod(Stats.MOVE_SLOW_SPEED_BONUS_MOD).modifyFlat("sc_low_profile", 1f, "低调行事")
        data.fleet.stats.detectedRangeMod.modifyMult("sc_low_profile", 1f-getBonus(data.fleet), "低调行事")
    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {

    }

    override fun onDeactivation(data: SCData) {
        data.fleet.stats.dynamic.getMod(Stats.MOVE_SLOW_SPEED_BONUS_MOD).unmodify("sc_low_profile")
       data.fleet.stats.detectedRangeMod.unmodify("sc_low_profile")
    }

}